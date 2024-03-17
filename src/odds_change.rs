use pyo3::prelude::*;

#[pyclass]
pub struct OddsChange {
    inner: neofoodclub::nfc::Change,
}

impl From<neofoodclub::nfc::Change> for OddsChange {
    fn from(change: neofoodclub::nfc::Change) -> Self {
        OddsChange { inner: change }
    }
}

#[pymethods]
impl OddsChange {
    #[getter]
    fn old(&self) -> u8 {
        self.inner.old
    }

    #[getter]
    fn new(&self) -> u8 {
        self.inner.new
    }

    #[getter]
    fn pirate(&self) -> u8 {
        self.inner.pirate
    }

    #[getter]
    fn arena(&self) -> u8 {
        self.inner.arena
    }

    #[getter]
    fn timestamp(&self) -> String {
        self.inner.t.to_string()
    }
}
