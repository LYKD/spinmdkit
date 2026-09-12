#include <array>
#include <cmath>
#include <cstddef>
#include <stdexcept>
#include <string>

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;
using Matrix = py::array_t<double, py::array::c_style | py::array::forcecast>;

void require_vectors(const py::buffer_info& info, const char* name) {
    if (info.ndim != 2 || info.shape[1] != 3) {
        throw std::invalid_argument(std::string(name) + " must have shape (number_of_atoms, 3)");
    }
}

py::array_t<double> row_norms(const Matrix& values) {
    const auto input = values.request();
    require_vectors(input, "values");
    const auto rows = static_cast<py::ssize_t>(input.shape[0]);
    py::array_t<double> output(rows);
    const auto in = values.unchecked<2>();
    auto out = output.mutable_unchecked<1>();
    for (py::ssize_t i = 0; i < rows; ++i) {
        out(i) = std::sqrt(in(i, 0) * in(i, 0) + in(i, 1) * in(i, 1) + in(i, 2) * in(i, 2));
    }
    return output;
}

py::array_t<double> row_sum(const Matrix& values) {
    const auto input = values.request();
    require_vectors(input, "values");
    const auto rows = static_cast<py::ssize_t>(input.shape[0]);
    py::array_t<double> output(3);
    const auto in = values.unchecked<2>();
    auto out = output.mutable_unchecked<1>();
    out(0) = 0.0;
    out(1) = 0.0;
    out(2) = 0.0;
    for (py::ssize_t i = 0; i < rows; ++i) {
        out(0) += in(i, 0);
        out(1) += in(i, 1);
        out(2) += in(i, 2);
    }
    return output;
}

py::array_t<double> row_cross(const Matrix& left, const Matrix& right) {
    const auto left_info = left.request();
    const auto right_info = right.request();
    require_vectors(left_info, "left");
    require_vectors(right_info, "right");
    if (left_info.shape != right_info.shape) {
        throw std::invalid_argument("left and right must have the same shape");
    }
    const auto rows = static_cast<py::ssize_t>(left_info.shape[0]);
    py::array_t<double> output({rows, static_cast<py::ssize_t>(3)});
    const auto a = left.unchecked<2>();
    const auto b = right.unchecked<2>();
    auto out = output.mutable_unchecked<2>();
    for (py::ssize_t i = 0; i < rows; ++i) {
        out(i, 0) = a(i, 1) * b(i, 2) - a(i, 2) * b(i, 1);
        out(i, 1) = a(i, 2) * b(i, 0) - a(i, 0) * b(i, 2);
        out(i, 2) = a(i, 0) * b(i, 1) - a(i, 1) * b(i, 0);
    }
    return output;
}

PYBIND11_MODULE(_core, module) {
    module.doc() = "SpinMDKit C++17 vector kernels";
    module.def("row_norms", &row_norms, py::arg("values"));
    module.def("row_sum", &row_sum, py::arg("values"));
    module.def("row_cross", &row_cross, py::arg("left"), py::arg("right"));
#ifdef VERSION_INFO
    module.attr("__version__") = VERSION_INFO;
#else
    module.attr("__version__") = "dev";
#endif
}
