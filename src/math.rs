use pyo3::{prelude::*, types::PyTuple};
use std::collections::HashMap;

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

    // represents each arena with the same pirate index filled.
    // PIR_IB[i] will accept pirates of index i (from 0 to 3) PIR_IB[0] = 0b10001000100010001000, PIR_IB[1] = 0b01000100010001000100, PIR_IB[2] = 0b00100010001000100010, PIR_IB[3] = 0b00010001000100010001
    // 0x88888 = (1, 1, 1, 1, 1), which is the first pirate in each arena, and so on.
    const PIR_IB: [u32; 4] = [0x88888, 0x44444, 0x22222, 0x11111];

    // 0xFFFFF = 0b11111111111111111111 (20 '1's), will accept all pirates
    const CONVERT_PIR_IB: [u32; 5] = [0xFFFFF, 0x88888, 0x44444, 0x22222, 0x11111];

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
    fn ib_doable(binary: u32) -> bool {
        // checks if there are possible winning combinations for ib
        for mask in Math::BIT_MASKS.iter() {
            if binary & mask == 0 {
                return false;
            }
        }
        true
    }

    #[staticmethod]
    fn ib_prob(binary: u32, probabilities: [[f64; 5]; 5]) -> f64 {
        // computes the probability that the winning combination is accepted by ib
        let mut total_prob: f64 = 1.0;
        for (x, bit_mask) in Math::BIT_MASKS.iter().enumerate() {
            let mut ar_prob: f64 = 0.0;
            for (y, pir_ib) in Math::PIR_IB.iter().enumerate() {
                if binary & bit_mask & pir_ib > 0 {
                    ar_prob += probabilities[x][y + 1];
                }
            }
            total_prob *= ar_prob;
        }
        total_prob
    }

    #[staticmethod]
    fn expand_ib_object(bets: Vec<Vec<u8>>, bet_odds: Vec<u32>) -> HashMap<u32, u32> {
        // makes a dict of permutations of the pirates + odds
        // this is why the bet table could be very long

        let mut bets_to_ib: HashMap<u32, u32> = HashMap::new();

        for (key, bet_value) in bets.iter().enumerate() {
            let mut ib: u32 = 0;
            for (&v, m) in bet_value.iter().zip(Math::BIT_MASKS.into_iter()) {
                ib |= Math::CONVERT_PIR_IB[v as usize] & m;
            }
            *bets_to_ib.entry(ib).or_insert(0) += bet_odds[key];
        }

        // filters down the doable bets from the permutations above
        let mut res: HashMap<u32, u32> = HashMap::new();
        res.insert(0xFFFFF, 0);
        let mut bets_to_ib: Vec<_> = bets_to_ib.into_iter().collect();
        bets_to_ib.sort();
        for (ib_bet, winnings) in bets_to_ib.into_iter() {
            let drained_elements: Vec<_> = res
                .keys()
                .copied()
                .filter(|ib_key| Math::ib_doable(ib_bet & ib_key))
                .collect();
            for mut ib_key in drained_elements.into_iter() {
                let com = ib_bet & ib_key;
                let val_key = res.remove(&ib_key).unwrap();
                res.insert(com, winnings + val_key);
                for ar in Math::BIT_MASKS {
                    let tst = ib_key ^ (com & ar);
                    if !Math::ib_doable(tst) {
                        continue;
                    }
                    res.insert(tst, val_key);
                    ib_key = (ib_key & !ar) | (com & ar);
                }
            }
        }
        res
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
