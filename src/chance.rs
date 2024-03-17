use pyo3::prelude::*;

#[pyclass]
pub struct Chance {
    inner: neofoodclub::chance::Chance,
}

impl From<neofoodclub::chance::Chance> for Chance {
    fn from(chance: neofoodclub::chance::Chance) -> Self {
        Chance { inner: chance }
    }
}

#[pymethods]
impl Chance {
    #[getter]
    fn value(&self) -> u32 {
        self.inner.value
    }

    #[getter]
    fn probability(&self) -> f64 {
        self.inner.probability
    }

    #[getter]
    fn cumulative(&self) -> f64 {
        self.inner.cumulative
    }

    #[getter]
    fn tail(&self) -> f64 {
        self.inner.tail
    }
}
