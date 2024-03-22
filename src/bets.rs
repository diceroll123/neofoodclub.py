use neofoodclub::bets::BetAmounts;
use pyo3::{prelude::*, types::PyTuple};

use crate::{nfc::NeoFoodClub, odds::Odds};

#[pyclass]
pub struct Bets {
    pub inner: neofoodclub::bets::Bets,
}

impl From<neofoodclub::bets::Bets> for Bets {
    fn from(bets: neofoodclub::bets::Bets) -> Self {
        Bets { inner: bets }
    }
}

#[pymethods]
impl Bets {
    fn fill_bet_amounts(&mut self, nfc: &NeoFoodClub) {
        self.inner.fill_bet_amounts(&nfc.inner);
    }

    #[getter(bet_amounts)]
    fn get_amounts<'a>(&self, py: Python<'a>) -> PyResult<Option<&'a PyTuple>> {
        let elements = &self.inner.bet_amounts;

        match elements {
            Some(amounts) => Ok(Some(PyTuple::new(py, amounts))),
            None => Ok(None),
        }
    }

    fn remove_amounts(&mut self) {
        self.inner.bet_amounts = None;
    }

    fn set_amounts_with_hash(&mut self, hash: String) {
        self.inner
            .set_bet_amounts(&Some(BetAmounts::AmountHash(hash)));
    }

    fn set_amounts_with_int(&mut self, amount: u32) {
        self.inner
            .set_bet_amounts(&Some(BetAmounts::from_amount(amount, self.inner.len())));
    }

    fn set_amounts_with_list(&mut self, amounts: Vec<Option<u32>>) {
        self.inner
            .set_bet_amounts(&Some(BetAmounts::Amounts(amounts)));
    }

    #[getter]
    fn odds(&self) -> Odds {
        Odds::from(self.inner.odds.clone())
    }

    fn __len__(&self) -> usize {
        self.inner.len()
    }

    #[getter]
    fn binaries<'a>(&self, py: Python<'a>) -> PyResult<&'a PyTuple> {
        Ok(PyTuple::new(py, &self.inner.get_binaries()))
    }

    #[getter]
    fn bets_hash(&self) -> String {
        self.inner.bets_hash()
    }

    #[getter]
    fn amounts_hash(&self) -> Option<String> {
        self.inner.amounts_hash()
    }

    #[getter]
    fn is_bustproof(&self) -> bool {
        self.inner.is_bustproof()
    }

    #[getter]
    fn is_crazy(&self) -> bool {
        self.inner.is_crazy()
    }

    #[getter]
    fn is_gambit(&self) -> bool {
        self.inner.is_gambit()
    }

    fn is_guaranteed_win(&self, nfc: &NeoFoodClub) -> bool {
        self.inner.is_guaranteed_win(&nfc.inner)
    }

    fn odds_values(&self, nfc: &NeoFoodClub) -> Vec<u32> {
        self.inner.odds_values(&nfc.inner)
    }

    #[getter]
    fn indices<'a>(&self, py: Python<'a>) -> PyResult<&'a PyTuple> {
        let indicies = self.inner.get_indices();
        let py_indicies: Vec<&'a PyTuple> = indicies
            .iter()
            .map(|index| PyTuple::new(py, index))
            .collect();

        Ok(PyTuple::new(py, py_indicies))
    }

    fn net_expected(&self, nfc: &NeoFoodClub) -> f64 {
        self.inner.net_expected(&nfc.inner)
    }

    fn expected_return(&self, nfc: &NeoFoodClub) -> f64 {
        self.inner.expected_return(&nfc.inner)
    }

    fn __repr__(&self) -> String {
        format!(
            "<Bets bets_hash={:?} amounts_hash={:?}>",
            self.inner.bets_hash(),
            self.inner.amounts_hash()
        )
    }

    fn __eq__(&self, other: &Self) -> bool {
        self.inner.get_indices() == other.inner.get_indices()
    }

    pub fn make_url(&self, nfc: &NeoFoodClub, include_domain: bool, all_data: bool) -> String {
        self.inner.make_url(&nfc.inner, include_domain, all_data)
    }
}
