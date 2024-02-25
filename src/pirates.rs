use neofoodclub::pirates::PartialPirateThings;
use pyo3::prelude::*;

#[pyclass]
pub struct PartialPirate {
    inner: neofoodclub::pirates::PartialPirate,
}

#[pymethods]
impl PartialPirate {
    #[new]
    fn new(id: usize) -> Self {
        PartialPirate {
            inner: neofoodclub::pirates::PartialPirate { id },
        }
    }

    #[getter]
    fn id(&self) -> PyResult<usize> {
        Ok(self.inner.id)
    }
    #[getter]
    fn name(&self) -> PyResult<&str> {
        Ok(self.inner.get_name())
    }

    #[getter]
    fn image(&self) -> PyResult<String> {
        Ok(self.inner.get_image())
    }
}
