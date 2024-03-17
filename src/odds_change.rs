use pyo3::prelude::*;

use crate::nfc::NeoFoodClub;

#[pyclass]
pub struct OddsChange {
    inner: neofoodclub::oddschange::OddsChange,
}

impl From<neofoodclub::oddschange::OddsChange> for OddsChange {
    fn from(change: neofoodclub::oddschange::OddsChange) -> Self {
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
    fn pirate_index(&self) -> usize {
        self.inner.pirate_index()
    }

    #[getter]
    fn arena_index(&self) -> usize {
        self.inner.arena_index()
    }

    #[getter]
    fn arena(&self) -> &str {
        self.inner.arena()
    }

    #[getter]
    fn timestamp(&self) -> String {
        self.inner.t.to_string()
    }

    fn pirate(&self, nfc: &NeoFoodClub) -> crate::pirates::PartialPirate {
        crate::pirates::PartialPirate::new(self.inner.pirate_id(&nfc.inner))
    }
}
