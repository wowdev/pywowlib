#pragma once

#include <Python.h>

#include <string>

namespace python
{
  namespace detail
  {
    namespace
    {
      //! \note If compilation fails here, check Python documentation for the
      //! correct character to be used, and add that to the list.
      //! \see https://docs.python.org/3/c-api/arg.html
      template<typename> struct tuple_char_for_type;
      #define mk_tuple_char_for_type(c_, t_)                          \
        template<> struct tuple_char_for_type<t_> { static char const v = c_; }
      mk_tuple_char_for_type ('i', int);
      mk_tuple_char_for_type ('I', unsigned int);
      mk_tuple_char_for_type ('k', unsigned long);
      mk_tuple_char_for_type ('K', unsigned long long);
      mk_tuple_char_for_type ('s', char*);
      mk_tuple_char_for_type ('s', char const*);

      //! \note fixed length char arrays are usually used as c-style strings
      template<std::size_t N> struct tuple_char_for_type<char[N]> 
        : tuple_char_for_type<char*> {};
      template<std::size_t N> struct tuple_char_for_type<char const[N]> 
        : tuple_char_for_type<char const*> {};
      //! \note enums are int in c++03
      mk_tuple_char_for_type (tuple_char_for_type<int>::v, SFileInfoClass);
      //! \note HANDLE is supposed to be opaque, and we shouldn't serialize
      //! \what's behind the pointer, so we just serialize the pointer value.
      mk_tuple_char_for_type (tuple_char_for_type<std::uintptr_t>::v, HANDLE);
    }
  }

  namespace
  {
    template<typename T1>
    bool parse_tuple (PyObject* args, char const* fun, T1* v1) {
      std::string const format 
        ( std::string (1, detail::tuple_char_for_type<T1>::v) 
        + ':' + fun
        );
      return PyArg_ParseTuple (args, format.c_str(), v1);
    }
    template<typename T1, typename T2>
    bool parse_tuple (PyObject* args, char const* fun, T1* v1, T2* v2) {
      std::string const format 
        ( std::string (1, detail::tuple_char_for_type<T1>::v)
        + std::string (1, detail::tuple_char_for_type<T2>::v) 
        + ':' + fun
        );
      return PyArg_ParseTuple (args, format.c_str(), v1, v2);
    }
    template<typename T1, typename T2, typename T3>
    bool parse_tuple (PyObject* args, char const* fun, T1* v1, T2* v2, T3* v3) {
      std::string const format 
        ( std::string (1, detail::tuple_char_for_type<T1>::v)
        + std::string (1, detail::tuple_char_for_type<T2>::v) 
        + std::string (1, detail::tuple_char_for_type<T3>::v) 
        + ':' + fun
        );
      return PyArg_ParseTuple (args, format.c_str(), v1, v2, v3);
    }
    template<typename T1, typename T2, typename T3, typename T4>
    bool parse_tuple (PyObject* args, char const* fun, T1* v1, T2* v2, T3* v3, T4* v4) {
      std::string const format 
        ( std::string (1, detail::tuple_char_for_type<T1>::v)
        + std::string (1, detail::tuple_char_for_type<T2>::v) 
        + std::string (1, detail::tuple_char_for_type<T3>::v) 
        + std::string (1, detail::tuple_char_for_type<T4>::v) 
        + ':' + fun
        );
      return PyArg_ParseTuple (args, format.c_str(), v1, v2, v3, v4);
    }

    template<typename T1>
    PyObject* build_value (T1 const& v1)
    {
      std::string const format 
        ( std::string (1, detail::tuple_char_for_type<T1>::v) 
        );
      return Py_BuildValue (format.c_str(), v1);
    }
    template<>
    PyObject* build_value (std::pair<char*, int> const& v1)
    {
      std::string const format 
        ( "y#" 
        );
      return Py_BuildValue (format.c_str(), v1.first, v1.second);
    }
    template<typename T1, typename T2>
    PyObject* build_value (T1 const& v1, T2 const& v2)
    {
      std::string const format 
        ( std::string (1, detail::tuple_char_for_type<T1>::v) 
        + std::string (1, detail::tuple_char_for_type<T2>::v) 
        );
      return Py_BuildValue (format.c_str(), v1, v2);
    }
  }
}
