use pyo3::prelude::*;

#[pyclass]
pub struct Modifier {
    pub inner: neofoodclub::modifier::Modifier,
}

impl Modifier {
    pub fn from_modifier(modifier: neofoodclub::modifier::Modifier) -> Self {
        Modifier { inner: modifier }
    }
}

#[pymethods]
impl Modifier {
    #[getter]
    fn value(&self) -> i32 {
        self.inner.value
    }

    #[getter]
    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }
    #[getter]
    pub fn is_general(&self) -> bool {
        self.inner.is_general()
    }
    #[getter]
    pub fn is_opening_odds(&self) -> bool {
        self.inner.is_opening_odds()
    }
    #[getter]
    pub fn is_reverse(&self) -> bool {
        self.inner.is_reverse()
    }
    #[getter]
    pub fn is_charity_corner(&self) -> bool {
        self.inner.is_charity_corner()
    }
}
