use neofoodclub::pirates::PartialPirateThings;
use pyo3::{prelude::*, types::PyTuple};

use crate::nfc::NeoFoodClub;

#[pyclass]
pub struct PartialPirate {
    inner: neofoodclub::pirates::PartialPirate,
}

#[pymethods]
impl PartialPirate {
    #[new]
    pub fn new(id: usize) -> Self {
        PartialPirate {
            inner: neofoodclub::pirates::PartialPirate { id },
        }
    }

    #[getter]
    fn id(&self) -> usize {
        self.inner.id
    }

    #[getter]
    fn name(&self) -> &str {
        self.inner.get_name()
    }

    #[getter]
    fn image(&self) -> String {
        self.inner.get_image()
    }
}

#[pyclass]
pub struct Pirate {
    inner: neofoodclub::pirates::Pirate,
}

impl From<neofoodclub::pirates::Pirate> for Pirate {
    fn from(pirate: neofoodclub::pirates::Pirate) -> Self {
        Pirate { inner: pirate }
    }
}

#[pymethods]
impl Pirate {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (id, arena_id, index, current_odds, opening_odds, is_winner, pfa=None, nfa=None, fa=None))]
    fn new(
        id: u8,
        arena_id: u8,
        index: u8,
        current_odds: u8,
        opening_odds: u8,
        is_winner: bool,
        pfa: Option<u8>,
        nfa: Option<i8>,
        fa: Option<i8>,
    ) -> Self {
        Pirate {
            inner: neofoodclub::pirates::Pirate {
                id,
                arena_id,
                index,
                current_odds,
                opening_odds,
                pfa,
                nfa,
                fa,
                is_winner,
            },
        }
    }

    #[getter]
    fn id(&self) -> u8 {
        self.inner.id
    }

    #[getter]
    fn index(&self) -> u8 {
        self.inner.index
    }

    #[getter]
    fn name(&self) -> &str {
        self.inner.get_name()
    }

    #[getter]
    fn image(&self) -> String {
        self.inner.get_image()
    }

    #[getter]
    fn arena_id(&self) -> u8 {
        self.inner.arena_id
    }

    #[getter]
    fn binary(&self) -> u32 {
        self.inner.binary()
    }

    #[getter]
    fn current_odds(&self) -> u8 {
        self.inner.current_odds
    }

    #[getter]
    fn opening_odds(&self) -> u8 {
        self.inner.opening_odds
    }

    #[getter]
    fn pfa(&self) -> Option<u8> {
        self.inner.pfa
    }

    #[getter]
    fn nfa(&self) -> Option<i8> {
        self.inner.nfa
    }

    #[getter]
    fn fa(&self) -> Option<i8> {
        self.inner.fa
    }

    #[getter]
    fn is_winner(&self) -> bool {
        self.inner.is_winner
    }

    fn positive_foods<'a>(
        &self,
        nfc: &NeoFoodClub,
        py: Python<'a>,
    ) -> PyResult<Option<Bound<'a, PyTuple>>> {
        let elements = self.inner.positive_foods(&nfc.inner);

        match elements {
            Some(foods) => Ok(Some(PyTuple::new(py, foods)?)),
            None => Ok(None),
        }
    }

    fn negative_foods<'a>(
        &self,
        nfc: &NeoFoodClub,
        py: Python<'a>,
    ) -> PyResult<Option<Bound<'a, PyTuple>>> {
        let elements = self.inner.negative_foods(&nfc.inner);

        match elements {
            Some(foods) => Ok(Some(PyTuple::new(py, foods)?)),
            None => Ok(None),
        }
    }

    fn __eq__(&self, other: &Self) -> bool {
        self.inner.id == other.inner.id
            && self.inner.arena_id == other.inner.arena_id
            && self.inner.index == other.inner.index
    }

    fn __int__(&self) -> u32 {
        self.inner.binary()
    }
}
