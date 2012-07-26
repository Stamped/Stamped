/*
 * Stamped (dev@stamped.com)
 * Version 1.0
 * Copyright (c) 2011-2012 Stamped.com
 */

#include <Python.h>

#include <ctype.h>
#include <string.h>

typedef struct MatrixStruct {
    double* data;
    int nrows;
    int ncols;
} Matrix;

static inline int GetIndex(Matrix matrix, int row, int col)
{
    assert(row >= 0);
    assert(col >= 0);
    assert(row < matrix.nrows);
    assert(col < matrix.ncols);
    return row * matrix.ncols + col;
}

static double MatrixGet(Matrix matrix, int row, int col)
{
    return matrix.data[GetIndex(matrix, row, col)];
}

static void MatrixSet(Matrix matrix, int row, int col, double val)
{
    matrix.data[GetIndex(matrix, row, col)] = val;
}

static inline double min(double a, double b)
{
    return a < b ? a : b;
}

static int* ConvertListToArray(PyObject* list)
{
    size_t i, list_size;
    int* result;
    PyObject* item;
    list_size = PyList_Size(list);
    result = malloc(sizeof(int) * (list_size + 1));
    for (i = 0; i < list_size; ++i) {
        item = PyList_GetItem(list, i);
        result[i] = (int) PyInt_AsLong(item);
    }
    result[list_size] = -1;
    return result;
}

static int FindIndex(int* list, int value)
{
    int list_val;
    int i = 0;
    for (i = 0; ; ++i) {
        list_val = list[i];
        if (list_val == value)
            return i;
        if (list_val == -1)
            return -1;
    }
}

static const char* PUNCTUATION_AND_SPACES = " .,:;()[]-_\"'?";
static double GetSkipCost(char c)
{
    if (strchr(PUNCTUATION_AND_SPACES, c))
        return 0.2;
    return 1.0;
}

static double GetCmpCost(char c1, char c2) {
    if (c1 == c2)
        return 0;
    if (tolower(c1) == tolower(c2))
        return 0.05;
    if (strchr(PUNCTUATION_AND_SPACES, c1) && strchr(PUNCTUATION_AND_SPACES, c2))
        return 0.25;
    return 2;
}

static double GetAndDelete(PyObject* value)
{
    double result = PyFloat_AsDouble(value);
    Py_DECREF(value);
    return result;
}

static PyObject* GetDifference(PyObject* cls, PyObject* args)
{
    int i, j, nrows, ncols, row_start, col_start, skip_begin;
    double least_penalty, cost;
    const char* s1;
    const char* s2;
    PyObject* starts1_list;
    PyObject* ends1_list;
    PyObject* starts2_list;
    PyObject* ends2_list;
    int* starts1;
    int* starts2;
    int* ends1;
    int* ends2;
    PyObject* skip_prefix_cost_fn;
    PyObject* skip_suffix_cost_fn;
    PyObject* skip_word_cost_fn;
    PyObject* call_args;

    if (!PyArg_ParseTuple(args, "ssOOOOOOO", &s1, &s2, &starts1_list, &ends1_list,
                &starts2_list, &ends2_list, &skip_prefix_cost_fn,
                &skip_suffix_cost_fn, &skip_word_cost_fn))
        return NULL;
    nrows = strlen(s1) + 1;
    ncols = strlen(s2) + 1;
    
    starts1 = ConvertListToArray(starts1_list);
    ends1 = ConvertListToArray(ends1_list);
    starts2 = ConvertListToArray(starts2_list);
    ends2 = ConvertListToArray(ends2_list);
    Matrix matrix = {malloc(nrows * ncols * sizeof(double)), nrows, ncols};
    memset(matrix.data, 0, nrows * ncols * sizeof(double));
    for (i = 0; i < nrows; ++i) {
        for (j = 0; j < ncols; ++j) {
            if (i == 0 && j == 0)
                continue;
            least_penalty = 1000000;
            row_start = FindIndex(starts1, i);
            col_start = FindIndex(starts2, j);

            // If we're at the start of a new word, consider cutting the previous out.
            if (row_start > 0 && col_start >= 0) {
                skip_begin = starts1[row_start-1];
                call_args = Py_BuildValue("(sii)", s1, skip_begin, starts1[row_start]);
                cost = GetAndDelete(PyObject_Call(skip_word_cost_fn, call_args, NULL));
                Py_DECREF(call_args);
                least_penalty = min(least_penalty, cost + MatrixGet(matrix, skip_begin, j));
            }
            if (col_start > 0 && row_start >= 0) {
                skip_begin = starts2[col_start-1];
                call_args = Py_BuildValue("(sii)", s2, skip_begin, starts2[col_start]);
                cost = GetAndDelete(PyObject_Call(skip_word_cost_fn, call_args, NULL));
                Py_DECREF(call_args);
                least_penalty = min(least_penalty, cost + MatrixGet(matrix, i, skip_begin));
            }
            
            // Handle cutting off the entire string1 or string2 to date as an unwanted prefix.
            if (j == 0 && row_start >= 0 && i != 0) {
                call_args = Py_BuildValue("(si)", s1, i);
                cost = GetAndDelete(PyObject_Call(skip_prefix_cost_fn, call_args, NULL));
                Py_DECREF(call_args);
                least_penalty = min(least_penalty, cost);
            }
            if (i == 0 && col_start >= 0 && j != 0) {
                call_args = Py_BuildValue("(si)", s2, j);
                cost = GetAndDelete(PyObject_Call(skip_prefix_cost_fn, call_args, NULL));
                Py_DECREF(call_args);
                least_penalty = min(least_penalty, cost);
            }

            // Handle the case where we want to just skip a character in one string or the other. Expensive.
            if (i)
                least_penalty = min(least_penalty, GetSkipCost(s1[i-1]) + MatrixGet(matrix, i-1, j));
            if (j)
                least_penalty = min(least_penalty, GetSkipCost(s2[j-1]) + MatrixGet(matrix, i, j-1));
            
            // Handle the case where we want to just progress a character in each string.
            if (i && j)
                least_penalty = min(least_penalty, GetCmpCost(s1[i-1], s2[j-1]) + MatrixGet(matrix, i-1, j-1));

            MatrixSet(matrix, i, j, least_penalty);
        }
    }
    least_penalty = MatrixGet(matrix, nrows-1, ncols-1);
    for (i = 0; ends1[i] != -1; ++i) {
        skip_begin = ends1[i];
        call_args = Py_BuildValue("(si)", s1, skip_begin);
        cost = GetAndDelete(PyObject_Call(skip_suffix_cost_fn, call_args, NULL));
        Py_DECREF(call_args);
        least_penalty = min(least_penalty, cost + MatrixGet(matrix, skip_begin, ncols-1));
    }
    for (i = 0; ends2[i] != -1; ++i) {
        skip_begin = ends2[i];
        call_args = Py_BuildValue("(si)", s2, skip_begin);
        cost = GetAndDelete(PyObject_Call(skip_suffix_cost_fn, call_args, NULL));
        Py_DECREF(call_args);
        least_penalty = min(least_penalty, cost + MatrixGet(matrix, nrows-1, skip_begin));
    }

    free(matrix.data);
    free(starts1);
    free(ends1);
    free(starts2);
    free(ends2);
    return PyFloat_FromDouble(least_penalty);
}

static PyMethodDef MODULE_METHODS[] = {
    {"get_difference", GetDifference, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL}  /* Sentinel */
};

PyMODINIT_FUNC initfastcompare(void)
{
    Py_InitModule("fastcompare", MODULE_METHODS);
}
