use pyo3::prelude::*;

use crate::chance::Chance;

#[pyclass]
pub struct Odds {
    inner: neofoodclub::odds::Odds,
}

impl Odds {
    pub fn from_odds(odds: neofoodclub::odds::Odds) -> Self {
        Odds { inner: odds }
    }
}

#[pymethods]
impl Odds {
    #[getter]
    fn best(&self) -> Chance {
        Chance::from_chance(self.inner.best.clone())
    }

    #[getter]
    fn bust(&self) -> Option<Chance> {
        self.inner.bust.clone().map(|c| Chance::from_chance(c))
    }

    #[getter]
    fn most_likely_winner(&self) -> Chance {
        Chance::from_chance(self.inner.most_likely_winner.clone())
    }

    #[getter]
    fn partial_rate(&self) -> f64 {
        self.inner.partial_rate
    }

    #[getter]
    fn chances(&self) -> Vec<Chance> {
        self.inner
            .chances
            .iter()
            .map(|c| Chance::from_chance(c.clone()))
            .collect()
    }
}
