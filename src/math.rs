use pyo3::{prelude::*, types::PyTuple};

use crate::chance::Chance;

// WARNING: the literal integers in this file switches between hex and binary willy-nilly, mostly for readability.

#[pyclass]
pub struct Math;

#[pymethods]
impl Math {
    #[classattr]
    const BIT_MASKS: [u32; 5] = neofoodclub::math::BIT_MASKS;

    #[classattr]
    pub const BET_AMOUNT_MIN: u32 = 50;

    #[classattr]
    pub const BET_AMOUNT_MAX: u32 = 70304;

    #[staticmethod]
    fn pirate_binary(index: u8, arena: u8) -> u32 {
        neofoodclub::math::pirate_binary(index, arena)
    }

    #[staticmethod]
    fn pirates_binary(bets_indices: [u8; 5]) -> u32 {
        neofoodclub::math::pirates_binary(bets_indices)
    }

    #[staticmethod]
    fn binary_to_indices(py: Python, binary: u32) -> PyResult<&PyTuple> {
        let elements = neofoodclub::math::binary_to_indices(binary);
        Ok(PyTuple::new(py, elements))
    }

    #[staticmethod]
    fn bets_hash_to_bet_indices<'a>(py: Python<'a>, bets_hash: &'a str) -> PyResult<&'a PyTuple> {
        let elements = neofoodclub::math::bets_hash_to_bet_indices(bets_hash);
        Ok(PyTuple::new(py, elements))
    }

    #[staticmethod]
    fn bet_amounts_to_amounts_hash(bet_amounts: Vec<u32>) -> String {
        neofoodclub::math::bet_amounts_to_amounts_hash(&bet_amounts)
    }

    #[staticmethod]
    fn bets_hash_value(bets_indices: Vec<[u8; 5]>) -> String {
        neofoodclub::math::bets_hash_value(bets_indices)
    }

    #[staticmethod]
    fn amounts_hash_to_bet_amounts<'a>(
        py: Python<'a>,
        amounts_hash: &'a str,
    ) -> PyResult<&'a PyTuple> {
        let elements = neofoodclub::math::amounts_hash_to_bet_amounts(amounts_hash);
        Ok(PyTuple::new(py, elements))
    }

    #[staticmethod]
    fn bets_hash_to_bet_binaries<'a>(py: Python<'a>, bets_hash: &'a str) -> PyResult<&'a PyTuple> {
        let elements = neofoodclub::math::bets_hash_to_bet_binaries(bets_hash);
        Ok(PyTuple::new(py, elements))
    }

    #[staticmethod]
    fn bets_hash_to_bets_count(bets_hash: &str) -> usize {
        neofoodclub::math::bets_hash_to_bets_count(bets_hash)
    }

    #[staticmethod]
    fn bets_indices_to_bet_binaries<'a>(
        py: Python<'a>,
        bets_indices: Vec<[u8; 5]>,
    ) -> PyResult<&'a PyTuple> {
        let elements = neofoodclub::math::bets_indices_to_bet_binaries(bets_indices);
        Ok(PyTuple::new(py, elements))
    }

    #[staticmethod]
    fn build_chance_objects<'a>(
        py: Python<'a>,
        bets: Vec<[u8; 5]>,
        bet_odds: Vec<u32>,
        probabilities: [[f64; 5]; 5],
    ) -> PyResult<&'a PyTuple> {
        let elements = neofoodclub::math::build_chance_objects(&bets, &bet_odds, probabilities);

        let py_structs: Vec<PyObject> = elements
            .into_iter()
            .map(|chance| {
                let chance = Chance {
                    value: chance.value,
                    probability: chance.probability,
                    cumulative: chance.cumulative,
                    tail: chance.tail,
                };
                chance.into_py(py)
            })
            .collect();

        Ok(PyTuple::new(py, py_structs))
    }
}
