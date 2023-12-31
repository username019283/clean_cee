# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: scipy\io\matlab\mio5.pyc
# Compiled at: 2013-02-16 13:27:30
""" Classes for read / write of matlab (TM) 5 files

The matfile specification last found here:

http://www.mathworks.com/access/helpdesk/help/pdf_doc/matlab/matfile_format.pdf

(as of December 5 2008)
"""
from __future__ import division, print_function, absolute_import
import os, time, sys, zlib
from io import BytesIO
import warnings, numpy as np
from numpy.compat import asbytes, asstr
import scipy.sparse
from scipy.lib.six import string_types
from . import byteordercodes as boc
from .miobase import MatFileReader, docfiller, matdims, read_dtype, arr_to_chars, arr_dtype_number, MatWriteError, MatReadError, MatReadWarning
from .mio5_utils import VarReader5
from .mio5_params import MatlabObject, MatlabFunction, MDTYPES, NP_TO_MTYPES, NP_TO_MXTYPES, miCOMPRESSED, miMATRIX, miINT8, miUTF8, miUINT32, mxCELL_CLASS, mxSTRUCT_CLASS, mxOBJECT_CLASS, mxCHAR_CLASS, mxSPARSE_CLASS, mxDOUBLE_CLASS, mclass_info, mclass_dtypes_template

class MatFile5Reader(MatFileReader):
    """ Reader for Mat 5 mat files
    Adds the following attribute to base class

    uint16_codec - char codec to use for uint16 char arrays
        (defaults to system default codec)

    Uses variable reader that has the following stardard interface (see
    abstract class in ``miobase``::

       __init__(self, file_reader)
       read_header(self)
       array_from_header(self)

    and added interface::

       set_stream(self, stream)
       read_full_tag(self)

    """

    @docfiller
    def __init__(self, mat_stream, byte_order=None, mat_dtype=False, squeeze_me=False, chars_as_strings=True, matlab_compatible=False, struct_as_record=True, uint16_codec=None):
        """Initializer for matlab 5 file format reader

    %(matstream_arg)s
    %(load_args)s
    %(struct_arg)s
    uint16_codec : {None, string}
        Set codec to use for uint16 char arrays (e.g. 'utf-8').
        Use system default codec if None
        """
        super(MatFile5Reader, self).__init__(mat_stream, byte_order, mat_dtype, squeeze_me, chars_as_strings, matlab_compatible, struct_as_record)
        if not uint16_codec:
            uint16_codec = sys.getdefaultencoding()
        self.uint16_codec = uint16_codec
        self._file_reader = None
        self._matrix_reader = None
        return

    def guess_byte_order(self):
        """ Guess byte order.
        Sets stream pointer to 0 """
        self.mat_stream.seek(126)
        mi = self.mat_stream.read(2)
        self.mat_stream.seek(0)
        return mi == 'IM' and '<' or '>'

    def read_file_header(self):
        """ Read in mat 5 file header """
        hdict = {}
        hdr_dtype = MDTYPES[self.byte_order]['dtypes']['file_header']
        hdr = read_dtype(self.mat_stream, hdr_dtype)
        hdict['__header__'] = hdr['description'].item().strip(' \t\n\x00')
        v_major = hdr['version'] >> 8
        v_minor = hdr['version'] & 255
        hdict['__version__'] = '%d.%d' % (v_major, v_minor)
        return hdict

    def initialize_read(self):
        """ Run when beginning read of variables

        Sets up readers from parameters in `self`
        """
        self._file_reader = VarReader5(self)
        self._matrix_reader = VarReader5(self)

    def read_var_header(self):
        """ Read header, return header, next position

        Header has to define at least .name and .is_global

        Parameters
        ----------
        None

        Returns
        -------
        header : object
           object that can be passed to self.read_var_array, and that
           has attributes .name and .is_global
        next_position : int
           position in stream of next variable
        """
        mdtype, byte_count = self._file_reader.read_full_tag()
        if not byte_count > 0:
            raise ValueError('Did not read any bytes')
        next_pos = self.mat_stream.tell() + byte_count
        if mdtype == miCOMPRESSED:
            data = self.mat_stream.read(byte_count)
            dcor = zlib.decompressobj()
            stream = BytesIO(dcor.decompress(data))
            if not dcor.flush() == '':
                raise ValueError('Something wrong with byte stream.')
            del data
            self._matrix_reader.set_stream(stream)
            mdtype, byte_count = self._matrix_reader.read_full_tag()
        else:
            self._matrix_reader.set_stream(self.mat_stream)
        if not mdtype == miMATRIX:
            raise TypeError('Expecting miMATRIX type here, got %d' % mdtype)
        header = self._matrix_reader.read_header()
        return (header, next_pos)

    def read_var_array(self, header, process=True):
        """ Read array, given `header`

        Parameters
        ----------
        header : header object
           object with fields defining variable header
        process : {True, False} bool, optional
           If True, apply recursive post-processing during loading of
           array.

        Returns
        -------
        arr : array
           array with post-processing applied or not according to
           `process`.
        """
        return self._matrix_reader.array_from_header(header, process)

    def get_variables(self, variable_names=None):
        """ get variables from stream as dictionary

        variable_names   - optional list of variable names to get

        If variable_names is None, then get all variables in file
        """
        if isinstance(variable_names, string_types):
            variable_names = [
             variable_names]
        self.mat_stream.seek(0)
        self.initialize_read()
        mdict = self.read_file_header()
        mdict['__globals__'] = []
        while not self.end_of_stream():
            hdr, next_position = self.read_var_header()
            name = asstr(hdr.name)
            if name in mdict:
                warnings.warn('Duplicate variable name "%s" in stream - replacing previous with new\nConsider mio5.varmats_from_mat to split file into single variable files' % name, MatReadWarning, stacklevel=2)
            if name == '':
                name = '__function_workspace__'
                process = False
            else:
                process = True
            if variable_names and name not in variable_names:
                self.mat_stream.seek(next_position)
                continue
            try:
                res = self.read_var_array(hdr, process)
            except MatReadError as err:
                warnings.warn('Unreadable variable "%s", because "%s"' % (
                 name, err), Warning, stacklevel=2)
                res = 'Read error: %s' % err

            self.mat_stream.seek(next_position)
            mdict[name] = res
            if hdr.is_global:
                mdict['__globals__'].append(name)
            if variable_names:
                variable_names.remove(name)
                if len(variable_names) == 0:
                    break

        return mdict

    def list_variables(self):
        """ list variables from stream """
        self.mat_stream.seek(0)
        self.initialize_read()
        self.read_file_header()
        vars = []
        while not self.end_of_stream():
            hdr, next_position = self.read_var_header()
            name = asstr(hdr.name)
            if name == '':
                name = '__function_workspace__'
            shape = self._matrix_reader.shape_from_header(hdr)
            info = mclass_info.get(hdr.mclass, 'unknown')
            vars.append((name, shape, info))
            self.mat_stream.seek(next_position)

        return vars


def varmats_from_mat(file_obj):
    """ Pull variables out of mat 5 file as a sequence of mat file objects

    This can be useful with a difficult mat file, containing unreadable
    variables.  This routine pulls the variables out in raw form and puts them,
    unread, back into a file stream for saving or reading.  Another use is the
    pathological case where there is more than one variable of the same name in
    the file; this routine returns the duplicates, whereas the standard reader
    will overwrite duplicates in the returned dictionary.

    The file pointer in `file_obj` will be undefined.  File pointers for the
    returned file-like objects are set at 0.

    Parameters
    ----------
    file_obj : file-like
        file object containing mat file

    Returns
    -------
    named_mats : list
        list contains tuples of (name, BytesIO) where BytesIO is a file-like
        object containing mat file contents as for a single variable.  The
        BytesIO contains a string with the original header and a single var. If
        ``var_file_obj`` is an individual BytesIO instance, then save as a mat
        file with something like ``open('test.mat',
        'wb').write(var_file_obj.read())``

    Examples
    --------
    >>> import scipy.io

    BytesIO is from the ``io`` module in python 3, and is ``cStringIO`` for
    python < 3.

    >>> mat_fileobj = BytesIO()
    >>> scipy.io.savemat(mat_fileobj, {'b': np.arange(10), 'a': 'a string'})
    >>> varmats = varmats_from_mat(mat_fileobj)
    >>> sorted([name for name, str_obj in varmats])
    ['a', 'b']
    """
    rdr = MatFile5Reader(file_obj)
    file_obj.seek(0)
    hdr_len = MDTYPES[boc.native_code]['dtypes']['file_header'].itemsize
    raw_hdr = file_obj.read(hdr_len)
    file_obj.seek(0)
    rdr.initialize_read()
    mdict = rdr.read_file_header()
    next_position = file_obj.tell()
    named_mats = []
    while not rdr.end_of_stream():
        start_position = next_position
        hdr, next_position = rdr.read_var_header()
        name = asstr(hdr.name)
        file_obj.seek(start_position)
        byte_count = next_position - start_position
        var_str = file_obj.read(byte_count)
        out_obj = BytesIO()
        out_obj.write(raw_hdr)
        out_obj.write(var_str)
        out_obj.seek(0)
        named_mats.append((name, out_obj))

    return named_mats


def to_writeable(source):
    """ Convert input object ``source`` to something we can write

    Parameters
    ----------
    source : object

    Returns
    -------
    arr : ndarray

    Examples
    --------
    >>> to_writeable(np.array([1])) # pass through ndarrays
    array([1])
    >>> expected = np.array([(1, 2)], dtype=[('a', '|O8'), ('b', '|O8')])
    >>> np.all(to_writeable({'a':1,'b':2}) == expected)
    True
    >>> np.all(to_writeable({'a':1,'b':2, '_c':3}) == expected)
    True
    >>> np.all(to_writeable({'a':1,'b':2, 100:3}) == expected)
    True
    >>> np.all(to_writeable({'a':1,'b':2, '99':3}) == expected)
    True
    >>> class klass(object): pass
    >>> c = klass
    >>> c.a = 1
    >>> c.b = 2
    >>> np.all(to_writeable({'a':1,'b':2}) == expected)
    True
    >>> to_writeable([])
    array([], dtype=float64)
    >>> to_writeable(())
    array([], dtype=float64)
    >>> to_writeable(None)

    >>> to_writeable('a string').dtype.type == np.str_
    True
    >>> to_writeable(1)
    array(1)
    >>> to_writeable([1])
    array([1])
    >>> to_writeable([1])
    array([1])
    >>> to_writeable(object()) # not convertable

    dict keys with legal characters are convertible

    >>> to_writeable({'a':1})['a']
    array([1], dtype=object)

    but not with illegal characters

    >>> to_writeable({'1':1}) is None
    True
    >>> to_writeable({'_a':1}) is None
    True
    """
    if isinstance(source, np.ndarray):
        return source
    else:
        if source is None:
            return
        is_mapping = hasattr(source, 'keys') and hasattr(source, 'values') and hasattr(source, 'items')
        if not is_mapping and hasattr(source, '__dict__'):
            source = dict((key, value) for key, value in source.__dict__.items() if not key.startswith('_'))
            is_mapping = True
        if is_mapping:
            dtype = []
            values = []
            for field, value in source.items():
                if isinstance(field, string_types) and field[0] not in '_0123456789':
                    dtype.append((field, object))
                    values.append(value)

            if dtype:
                return np.array([tuple(values)], dtype)
            return
        narr = np.asanyarray(source)
        if narr.dtype.type in (np.object, np.object_) and narr.shape == () and narr == source:
            return
        return narr


NDT_FILE_HDR = MDTYPES[boc.native_code]['dtypes']['file_header']
NDT_TAG_FULL = MDTYPES[boc.native_code]['dtypes']['tag_full']
NDT_TAG_SMALL = MDTYPES[boc.native_code]['dtypes']['tag_smalldata']
NDT_ARRAY_FLAGS = MDTYPES[boc.native_code]['dtypes']['array_flags']

class VarWriter5(object):
    """ Generic matlab matrix writing class """
    mat_tag = np.zeros((), NDT_TAG_FULL)
    mat_tag['mdtype'] = miMATRIX

    def __init__(self, file_writer):
        self.file_stream = file_writer.file_stream
        self.unicode_strings = file_writer.unicode_strings
        self.long_field_names = file_writer.long_field_names
        self.oned_as = file_writer.oned_as
        self._var_name = None
        self._var_is_global = False
        return

    def write_bytes(self, arr):
        self.file_stream.write(arr.tostring(order='F'))

    def write_string(self, s):
        self.file_stream.write(s)

    def write_element(self, arr, mdtype=None):
        """ write tag and data """
        if mdtype is None:
            mdtype = NP_TO_MTYPES[arr.dtype.str[1:]]
        byte_count = arr.size * arr.itemsize
        if byte_count <= 4:
            self.write_smalldata_element(arr, mdtype, byte_count)
        else:
            self.write_regular_element(arr, mdtype, byte_count)
        return

    def write_smalldata_element(self, arr, mdtype, byte_count):
        tag = np.zeros((), NDT_TAG_SMALL)
        tag['byte_count_mdtype'] = (byte_count << 16) + mdtype
        tag['data'] = arr.tostring(order='F')
        self.write_bytes(tag)

    def write_regular_element(self, arr, mdtype, byte_count):
        tag = np.zeros((), NDT_TAG_FULL)
        tag['mdtype'] = mdtype
        tag['byte_count'] = byte_count
        self.write_bytes(tag)
        self.write_bytes(arr)
        bc_mod_8 = byte_count % 8
        if bc_mod_8:
            self.file_stream.write('\x00' * (8 - bc_mod_8))

    def write_header(self, shape, mclass, is_complex=False, is_logical=False, nzmax=0):
        """ Write header for given data options
        shape : sequence
           array shape
        mclass      - mat5 matrix class
        is_complex  - True if matrix is complex
        is_logical  - True if matrix is logical
        nzmax        - max non zero elements for sparse arrays

        We get the name and the global flag from the object, and reset
        them to defaults after we've used them
        """
        name = self._var_name
        is_global = self._var_is_global
        self._mat_tag_pos = self.file_stream.tell()
        self.write_bytes(self.mat_tag)
        af = np.zeros((), NDT_ARRAY_FLAGS)
        af['data_type'] = miUINT32
        af['byte_count'] = 8
        flags = is_complex << 3 | is_global << 2 | is_logical << 1
        af['flags_class'] = mclass | flags << 8
        af['nzmax'] = nzmax
        self.write_bytes(af)
        self.write_element(np.array(shape, dtype='i4'))
        name = np.asarray(name)
        if name == '':
            self.write_smalldata_element(name, miINT8, 0)
        else:
            self.write_element(name, miINT8)
        self._var_name = ''
        self._var_is_global = False

    def update_matrix_tag(self, start_pos):
        curr_pos = self.file_stream.tell()
        self.file_stream.seek(start_pos)
        self.mat_tag['byte_count'] = curr_pos - start_pos - 8
        self.write_bytes(self.mat_tag)
        self.file_stream.seek(curr_pos)

    def write_top(self, arr, name, is_global):
        """ Write variable at top level of mat file

        Parameters
        ----------
        arr : array-like
            array-like object to create writer for
        name : str, optional
            name as it will appear in matlab workspace
            default is empty string
        is_global : {False, True}, optional
            whether variable will be global on load into matlab
        """
        self._var_is_global = is_global
        self._var_name = name
        self.write(arr)

    def write(self, arr):
        """ Write `arr` to stream at top and sub levels

        Parameters
        ----------
        arr : array-like
            array-like object to create writer for
        """
        mat_tag_pos = self.file_stream.tell()
        if scipy.sparse.issparse(arr):
            self.write_sparse(arr)
            self.update_matrix_tag(mat_tag_pos)
            return
        else:
            narr = to_writeable(arr)
            if narr is None:
                raise TypeError('Could not convert %s (type %s) to array' % (
                 arr, type(arr)))
            if isinstance(narr, MatlabObject):
                self.write_object(narr)
            elif isinstance(narr, MatlabFunction):
                raise MatWriteError('Cannot write matlab functions')
            elif narr.dtype.fields:
                self.write_struct(narr)
            elif narr.dtype.hasobject:
                self.write_cells(narr)
            elif narr.dtype.kind in ('U', 'S'):
                if self.unicode_strings:
                    codec = 'UTF8'
                else:
                    codec = 'ascii'
                self.write_char(narr, codec)
            else:
                self.write_numeric(narr)
            self.update_matrix_tag(mat_tag_pos)
            return

    def write_numeric(self, arr):
        imagf = arr.dtype.kind == 'c'
        try:
            mclass = NP_TO_MXTYPES[arr.dtype.str[1:]]
        except KeyError:
            if imagf:
                arr = arr.astype('c128')
            else:
                arr = arr.astype('f8')
            mclass = mxDOUBLE_CLASS

        self.write_header(matdims(arr, self.oned_as), mclass, is_complex=imagf)
        if imagf:
            self.write_element(arr.real)
            self.write_element(arr.imag)
        else:
            self.write_element(arr)

    def write_char(self, arr, codec='ascii'):
        """ Write string array `arr` with given `codec`
        """
        if arr.size == 0 or np.all(arr == ''):
            shape = (0, ) * np.max([arr.ndim, 2])
            self.write_header(shape, mxCHAR_CLASS)
            self.write_smalldata_element(arr, miUTF8, 0)
            return
        arr = arr_to_chars(arr)
        shape = arr.shape
        self.write_header(shape, mxCHAR_CLASS)
        if arr.dtype.kind == 'U' and arr.size:
            n_chars = np.product(shape)
            st_arr = np.ndarray(shape=(), dtype=arr_dtype_number(arr, n_chars), buffer=arr.T.copy())
            st = st_arr.item().encode(codec)
            arr = np.ndarray(shape=(len(st),), dtype='S1', buffer=st)
        self.write_element(arr, mdtype=miUTF8)

    def write_sparse(self, arr):
        """ Sparse matrices are 2D
        """
        A = arr.tocsc()
        A.sort_indices()
        is_complex = A.dtype.kind == 'c'
        nz = A.nnz
        self.write_header(matdims(arr, self.oned_as), mxSPARSE_CLASS, is_complex=is_complex, nzmax=nz)
        self.write_element(A.indices.astype('i4'))
        self.write_element(A.indptr.astype('i4'))
        self.write_element(A.data.real)
        if is_complex:
            self.write_element(A.data.imag)

    def write_cells(self, arr):
        self.write_header(matdims(arr, self.oned_as), mxCELL_CLASS)
        A = np.atleast_2d(arr).flatten('F')
        for el in A:
            self.write(el)

    def write_struct(self, arr):
        self.write_header(matdims(arr, self.oned_as), mxSTRUCT_CLASS)
        self._write_items(arr)

    def _write_items(self, arr):
        fieldnames = [ f[0] for f in arr.dtype.descr ]
        length = max([ len(fieldname) for fieldname in fieldnames ]) + 1
        max_length = self.long_field_names and 64 or 32
        if length > max_length:
            raise ValueError('Field names are restricted to %d characters' % (max_length - 1))
        self.write_element(np.array([length], dtype='i4'))
        self.write_element(np.array(fieldnames, dtype='S%d' % length), mdtype=miINT8)
        A = np.atleast_2d(arr).flatten('F')
        for el in A:
            for f in fieldnames:
                self.write(el[f])

    def write_object(self, arr):
        """Same as writing structs, except different mx class, and extra
        classname element after header
        """
        self.write_header(matdims(arr, self.oned_as), mxOBJECT_CLASS)
        self.write_element(np.array(arr.classname, dtype='S'), mdtype=miINT8)
        self._write_items(arr)


class MatFile5Writer(object):
    """ Class for writing mat5 files """

    @docfiller
    def __init__(self, file_stream, do_compression=False, unicode_strings=False, global_vars=None, long_field_names=False, oned_as=None):
        """ Initialize writer for matlab 5 format files

        Parameters
        ----------
        %(do_compression)s
        %(unicode_strings)s
        global_vars : None or sequence of strings, optional
            Names of variables to be marked as global for matlab
        %(long_fields)s
        %(oned_as)s
        """
        self.file_stream = file_stream
        self.do_compression = do_compression
        self.unicode_strings = unicode_strings
        if global_vars:
            self.global_vars = global_vars
        else:
            self.global_vars = []
        self.long_field_names = long_field_names
        if oned_as is None:
            warnings.warn("Using oned_as default value ('column')" + " This will change to 'row' in future versions", FutureWarning, stacklevel=2)
            oned_as = 'column'
        self.oned_as = oned_as
        self._matrix_writer = None
        return

    def write_file_header(self):
        hdr = np.zeros((), NDT_FILE_HDR)
        hdr['description'] = 'MATLAB 5.0 MAT-file Platform: %s, Created on: %s' % (
         os.name, time.asctime())
        hdr['version'] = 256
        hdr['endian_test'] = np.ndarray(shape=(), dtype='S2', buffer=np.uint16(19785))
        self.file_stream.write(hdr.tostring())

    def put_variables(self, mdict, write_header=None):
        """ Write variables in `mdict` to stream

        Parameters
        ----------
        mdict : mapping
           mapping with method ``items`` returns name, contents pairs where
           ``name`` which will appear in the matlab workspace in file load, and
           ``contents`` is something writeable to a matlab file, such as a numpy
           array.
        write_header : {None, True, False}
           If True, then write the matlab file header before writing the
           variables.  If None (the default) then write the file header
           if we are at position 0 in the stream.  By setting False
           here, and setting the stream position to the end of the file,
           you can append variables to a matlab file
        """
        if write_header is None:
            write_header = self.file_stream.tell() == 0
        if write_header:
            self.write_file_header()
        self._matrix_writer = VarWriter5(self)
        for name, var in mdict.items():
            if name[0] == '_':
                continue
            is_global = name in self.global_vars
            if self.do_compression:
                stream = BytesIO()
                self._matrix_writer.file_stream = stream
                self._matrix_writer.write_top(var, asbytes(name), is_global)
                out_str = zlib.compress(stream.getvalue())
                tag = np.empty((), NDT_TAG_FULL)
                tag['mdtype'] = miCOMPRESSED
                tag['byte_count'] = len(out_str)
                self.file_stream.write(tag.tostring() + out_str)
            else:
                self._matrix_writer.write_top(var, asbytes(name), is_global)

        return