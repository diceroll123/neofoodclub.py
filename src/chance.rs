use pyo3::prelude::*;

#[derive(Debug, Clone)]
#[pyclass]
pub struct Chance {
    #[pyo3(get)]
    pub value: u32,
    #[pyo3(get)]
    pub probability: f64,
    #[pyo3(get)]
    pub cumulative: f64,
    #[pyo3(get)]
    pub tail: f64,
}
