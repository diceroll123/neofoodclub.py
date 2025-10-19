use pyo3::prelude::*;

use crate::chance::Chance;

#[pyclass]
pub struct Odds {
    inner: neofoodclub::odds::Odds,
}

impl From<neofoodclub::odds::Odds> for Odds {
    fn from(odds: neofoodclub::odds::Odds) -> Self {
        Odds { inner: odds }
    }
}

#[pymethods]
impl Odds {
    #[getter]
    fn best(&self) -> Chance {
        Chance::from(self.inner.best())
    }

    #[getter]
    fn bust(&self) -> Option<Chance> {
        self.inner.bust().map(|c| Chance::from(c))
    }

    #[getter]
    fn most_likely_winner(&self) -> Chance {
        Chance::from(self.inner.most_likely_winner())
    }

    #[getter]
    fn partial_rate(&self) -> f64 {
        self.inner.partial_rate()
    }

    #[getter]
    fn chances(&self) -> Vec<Chance> {
        self.inner
            .chances()
            .iter()
            .map(|c| Chance::from(c.clone()))
            .collect()
    }
}
