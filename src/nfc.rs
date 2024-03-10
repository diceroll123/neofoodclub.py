use pyo3::{
    prelude::*,
    types::{PyTuple, PyType},
};

use crate::{
    arena::{Arena, Arenas},
    bets::Bets,
    pirates::Pirate,
};

#[pyclass]
pub struct NeoFoodClub {
    pub inner: neofoodclub::nfc::NeoFoodClub,
}

#[pymethods]
impl NeoFoodClub {
    #[new]
    fn new(json: &str, bet_amount: Option<u32>) -> Self {
        NeoFoodClub {
            inner: neofoodclub::nfc::NeoFoodClub::from_json(json, bet_amount, None, None),
        }
    }

    #[classmethod]
    fn from_url(_cls: &PyType, url: &str, bet_amount: Option<u32>) -> Self {
        NeoFoodClub {
            inner: neofoodclub::nfc::NeoFoodClub::from_url(url, bet_amount, None, None),
        }
    }

    fn copy(&self) -> Self {
        NeoFoodClub {
            inner: self.inner.copy(),
        }
    }

    #[getter]
    fn arenas(&self) -> Arenas {
        let elements = self.inner.arenas.clone();
        Arenas::from_arenas(elements)
    }

    fn get_arena(&self, index: usize) -> Arena {
        let arena = self.inner.arenas.get_arena(index).expect("Invalid index");
        Arena::from_arena(arena)
    }

    #[getter(bet_amount)]
    fn get_bet_amount(&self) -> Option<u32> {
        self.inner.bet_amount
    }

    #[setter(bet_amount)]
    fn set_bet_amount(&mut self, bet_amount: Option<u32>) {
        self.inner.set_bet_amount(bet_amount);
    }

    #[getter]
    fn winners<'a>(&self, py: Python<'a>) -> PyResult<&'a PyTuple> {
        let elements = self.inner.winners();
        Ok(PyTuple::new(py, elements))
    }

    #[getter]
    fn winners_binary(&self) -> u32 {
        self.inner.winners_binary()
    }

    #[getter]
    fn is_over(&self) -> bool {
        self.inner.is_over()
    }

    #[getter]
    fn round(&self) -> u16 {
        self.inner.round()
    }

    #[getter]
    fn start(&self) -> Option<String> {
        self.inner.start()
    }

    #[getter]
    fn current_odds<'a>(&self, py: Python<'a>) -> PyResult<&'a PyTuple> {
        let elements = self.inner.current_odds();
        Ok(PyTuple::new(py, elements))
    }

    #[getter]
    fn opening_odds<'a>(&self, py: Python<'a>) -> PyResult<&'a PyTuple> {
        let elements = self.inner.opening_odds();
        Ok(PyTuple::new(py, elements))
    }

    #[getter]
    fn timestamp(&self) -> Option<String> {
        self.inner.timestamp()
    }

    #[getter]
    fn last_change(&self) -> Option<String> {
        self.inner.last_change()
    }

    #[getter]
    fn foods<'a>(&self, py: Python<'a>) -> PyResult<Option<&'a PyTuple>> {
        let elements = self.inner.foods();

        match elements {
            Some(e) => Ok(Some(PyTuple::new(py, e))),
            None => Ok(None),
        }
    }

    #[getter]
    fn max_amount_of_bets(&self) -> usize {
        self.inner.max_amount_of_bets()
    }

    #[getter]
    fn get_winning_pirates(&self) -> Option<Vec<Pirate>> {
        match self.inner.winning_pirates() {
            Some(pirates) => Some(pirates.iter().map(|p| Pirate::from_pirate(**p)).collect()),
            None => None,
        }
    }

    fn make_random_bets(&self) -> Bets {
        Bets::from_bets(self.inner.make_random_bets())
    }

    fn make_tenbet_bets(&self, pirates_binary: u32) -> Bets {
        Bets::from_bets(self.inner.make_tenbet_bets(pirates_binary))
    }

    fn make_max_ter_bets(&self) -> Bets {
        Bets::from_bets(self.inner.make_max_ter_bets())
    }

    fn make_gambit_bets(&self, pirates_binary: u32) -> Bets {
        Bets::from_bets(self.inner.make_gambit_bets(pirates_binary))
    }

    fn make_best_gambit_bets(&self) -> Bets {
        Bets::from_bets(self.inner.make_best_gambit_bets())
    }

    fn make_winning_gambit_bets(&self) -> Option<Bets> {
        match self.inner.make_winning_gambit_bets() {
            Some(bets) => Some(Bets::from_bets(bets)),
            None => None,
        }
    }

    fn make_random_gambit_bets(&self) -> Bets {
        Bets::from_bets(self.inner.make_random_gambit_bets())
    }

    fn make_crazy_bets(&self) -> Bets {
        Bets::from_bets(self.inner.make_crazy_bets())
    }

    fn make_bustproof_bets(&self) -> Option<Bets> {
        match self.inner.make_bustproof_bets() {
            Some(bets) => Some(Bets::from_bets(bets)),
            None => None,
        }
    }

    fn make_bets_from_hash(&self, bets_hash: &str) -> Bets {
        Bets::from_bets(self.inner.make_bets_from_hash(bets_hash))
    }

    fn make_bets_from_binaries(&self, binaries: Vec<u32>) -> Bets {
        Bets::from_bets(self.inner.make_bets_from_binaries(binaries))
    }

    fn make_bets_from_indices(&self, indices: Vec<[u8; 5]>) -> Bets {
        Bets::from_bets(self.inner.make_bets_from_indices(indices))
    }

    fn get_win_units(&self, bets: &Bets) -> u32 {
        self.inner.get_win_units(&bets.inner)
    }

    fn get_win_np(&self, bets: &Bets) -> u32 {
        self.inner.get_win_np(&bets.inner)
    }

    fn __repr__(&self) -> String {
        format!(
            "<NeoFoodClub round={:?} bet_amount={:?}>",
            self.inner.round(),
            self.inner.bet_amount
        )
    }
}
