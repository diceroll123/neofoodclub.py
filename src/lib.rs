use itertools::iproduct;
use neofoodclub::math::BET_AMOUNT_MAX;
use neofoodclub::math::BET_AMOUNT_MIN;
use numpy::{ndarray::Array1, PyArray1, ToPyArray};
use pyo3::{prelude::*, types::PyTuple};
use std::collections::{BTreeMap, HashMap};

// WARNING: the literal integers in this file switches between hex and binary willy-nilly, mostly for readability.

static BIT_MASKS: [u32; 5] = neofoodclub::math::BIT_MASKS;

// represents each arena with the same pirate index filled.
// PIR_IB[i] will accept pirates of index i (from 0 to 3) PIR_IB[0] = 0b10001000100010001000, PIR_IB[1] = 0b01000100010001000100, PIR_IB[2] = 0b00100010001000100010, PIR_IB[3] = 0b00010001000100010001
// 0x88888 = (1, 1, 1, 1, 1), which is the first pirate in each arena, and so on.
const PIR_IB: [u32; 4] = [0x88888, 0x44444, 0x22222, 0x11111];

// 0xFFFFF = 0b11111111111111111111 (20 '1's), will accept all pirates
const CONVERT_PIR_IB: [u32; 5] = [0xFFFFF, 0x88888, 0x44444, 0x22222, 0x11111];

#[pyclass]
struct Chance {
    #[pyo3(get)]
    value: u32,
    #[pyo3(get)]
    probability: f64,
    #[pyo3(get)]
    cumulative: f64,
    #[pyo3(get)]
    tail: f64,
}

#[pyfunction]
fn pirate_binary(index: u8, arena: u8) -> u32 {
    neofoodclub::math::pirate_binary(index, arena)
}

#[pyfunction]
fn pirates_binary(bets_indices: [u8; 5]) -> u32 {
    neofoodclub::math::pirates_binary(bets_indices)
}

#[pyfunction]
fn binary_to_indices(py: Python, binary: u32) -> PyResult<&PyTuple> {
    let elements = neofoodclub::math::binary_to_indices(binary);
    Ok(PyTuple::new(py, elements))
}

#[pyfunction]
fn bets_hash_to_bet_indices<'a>(py: Python<'a>, bets_hash: &'a str) -> PyResult<&'a PyTuple> {
    let elements = neofoodclub::math::bets_hash_to_bet_indices(bets_hash);
    Ok(PyTuple::new(py, elements))
}

#[pyfunction]
fn bet_amounts_to_amounts_hash(bet_amounts: Vec<u32>) -> String {
    neofoodclub::math::bet_amounts_to_amounts_hash(&bet_amounts)
}

#[pyfunction]
fn bets_hash_value(bets_indices: Vec<[u8; 5]>) -> String {
    neofoodclub::math::bets_hash_value(bets_indices)
}

#[pyfunction]
fn amounts_hash_to_bet_amounts<'a>(py: Python<'a>, amounts_hash: &'a str) -> PyResult<&'a PyTuple> {
    let elements = neofoodclub::math::amounts_hash_to_bet_amounts(amounts_hash);
    Ok(PyTuple::new(py, elements))
}

#[pyfunction]
fn bets_hash_to_bet_binaries<'a>(py: Python<'a>, bets_hash: &'a str) -> PyResult<&'a PyTuple> {
    let elements = neofoodclub::math::bets_hash_to_bet_binaries(bets_hash);
    Ok(PyTuple::new(py, elements))
}

#[pyfunction]
fn bets_hash_to_bets_count(bets_hash: &str) -> usize {
    neofoodclub::math::bets_hash_to_bets_count(bets_hash)
}

#[pyfunction]
fn bets_indices_to_bet_binaries<'a>(
    py: Python<'a>,
    bets_indices: Vec<[u8; 5]>,
) -> PyResult<&'a PyTuple> {
    let elements = neofoodclub::math::bets_indices_to_bet_binaries(bets_indices);
    Ok(PyTuple::new(py, elements))
}

#[pyfunction]
fn make_probabilities(opening_odds: Vec<Vec<u32>>) -> Vec<Vec<f64>> {
    let mut std: [[f64; 5]; 5] = [[1.0, 0.0, 0.0, 0.0, 0.0]; 5];
    let mut min: [[f64; 5]; 5] = [[1.0, 0.0, 0.0, 0.0, 0.0]; 5];
    let mut max: [[f64; 5]; 5] = [[1.0, 0.0, 0.0, 0.0, 0.0]; 5];
    // let mut used: [[f64; 5]; 5] = [[1.0, 0.0, 0.0, 0.0, 0.0]; 5];
    // turns out we only use _std values in the python implementation of NFC
    // keeping the _used math to avoid confusion between NFC impls
    // however, if we use this Rust code on the frontend of neofood.club
    // that's the best time to expose this.

    for arena in 0..5 {
        let mut min_prob: f64 = 0.0;
        let mut max_prob: f64 = 0.0;

        for pirate in 1..5 {
            let pirate_odd: u32 = opening_odds[arena][pirate];
            if pirate_odd == 13 {
                min[arena][pirate] = 0.0;
                max[arena][pirate] = 1.0 / 13.0;
            } else if pirate_odd == 2 {
                min[arena][pirate] = 1.0 / 3.0;
                max[arena][pirate] = 1.0;
            } else {
                let p_o: f64 = pirate_odd as f64;
                min[arena][pirate] = 1.0 / (1.0 + p_o);
                max[arena][pirate] = 1.0 / p_o;
            }

            min_prob += min[arena][pirate];
            max_prob += max[arena][pirate];
        }

        for pirate in 1..5 {
            let min_original: f64 = min[arena][pirate];
            let max_original: f64 = max[arena][pirate];

            min[arena][pirate] = f64::max(min_original, 1.0 + max_original - max_prob);
            max[arena][pirate] = f64::min(max_original, 1.0 + min_original - min_prob);
            std[arena][pirate] = match opening_odds[arena][pirate] {
                13 => 0.05,
                _ => (min[arena][pirate] + max[arena][pirate]) / 2.0,
            };
        }

        for rectify_level in 2..13 {
            let mut rectify_count: f64 = 0.0;
            let mut std_total: f64 = 0.0;
            let mut rectify_value: f64 = 0.0;
            let mut max_rectify_value: f64 = 1.0;

            for pirate in 1..5 {
                std_total += std[arena][pirate];
                if opening_odds[arena][pirate] <= rectify_level {
                    rectify_count += 1.0;
                    rectify_value += std[arena][pirate] - min[arena][pirate];
                    max_rectify_value =
                        f64::min(max_rectify_value, max[arena][pirate] - min[arena][pirate]);
                }
            }

            if std_total == 1.0 {
                break;
            }

            if !(std_total - rectify_value > 1.0
                || rectify_count == 0.0
                || max_rectify_value * rectify_count < rectify_value + 1.0 - std_total)
            {
                rectify_value += 1.0 - std_total;
                rectify_value /= rectify_count;
                for pirate in 1..5 {
                    if opening_odds[arena][pirate] <= rectify_level {
                        std[arena][pirate] = min[arena][pirate] + rectify_value;
                    }
                }
                break;
            }
        }

        // let mut return_sum = 0.0;
        // for pirate in 1..5 {
        //     used[arena][pirate] = std[arena][pirate];
        //     return_sum += used[arena][pirate];
        // }

        // for pirate in 1..5 {
        //     used[arena][pirate] /= return_sum;
        // }
    }

    // convert std to a vector of vectors before returning
    std.iter().map(|&e| e.to_vec()).collect()
}

fn ib_doable(binary: u32) -> bool {
    // checks if there are possible winning combinations for ib
    for mask in BIT_MASKS.iter() {
        if binary & mask == 0 {
            return false;
        }
    }
    true
}

fn ib_prob(binary: u32, probabilities: [[f64; 5]; 5]) -> f64 {
    // computes the probability that the winning combination is accepted by ib
    let mut total_prob: f64 = 1.0;
    for (x, bit_mask) in BIT_MASKS.iter().enumerate() {
        let mut ar_prob: f64 = 0.0;
        for (y, pir_ib) in PIR_IB.iter().enumerate() {
            if binary & bit_mask & pir_ib > 0 {
                ar_prob += probabilities[x][y + 1];
            }
        }
        total_prob *= ar_prob;
    }
    total_prob
}

fn expand_ib_object(bets: Vec<Vec<u8>>, bet_odds: Vec<u32>) -> HashMap<u32, u32> {
    // makes a dict of permutations of the pirates + odds
    // this is why the bet table could be very long

    let mut bets_to_ib: HashMap<u32, u32> = HashMap::new();

    for (key, bet_value) in bets.iter().enumerate() {
        let mut ib: u32 = 0;
        for (&v, m) in bet_value.iter().zip(BIT_MASKS.into_iter()) {
            ib |= CONVERT_PIR_IB[v as usize] & m;
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
            .filter(|ib_key| ib_doable(ib_bet & ib_key))
            .collect();
        for mut ib_key in drained_elements.into_iter() {
            let com = ib_bet & ib_key;
            let val_key = res.remove(&ib_key).unwrap();
            res.insert(com, winnings + val_key);
            for ar in BIT_MASKS {
                let tst = ib_key ^ (com & ar);
                if !ib_doable(tst) {
                    continue;
                }
                res.insert(tst, val_key);
                ib_key = (ib_key & !ar) | (com & ar);
            }
        }
    }
    res
}

#[pyfunction]
fn make_round_dicts<'py>(
    py: Python<'py>,
    stds: Vec<Vec<f64>>,
    odds: Vec<Vec<u32>>,
) -> (
    &PyArray1<u32>,
    &PyArray1<f64>,
    &PyArray1<u32>,
    &PyArray1<f64>,
    &PyArray1<u32>,
) {
    let mut _bins: Array1<u32> = Array1::zeros(3124);
    let mut _stds: Array1<f64> = Array1::zeros(3124);
    let mut _odds: Array1<u32> = Array1::zeros(3124);
    let mut _ers: Array1<f64> = Array1::zeros(3124);
    let mut _maxbets: Array1<u32> = Array1::zeros(3124);

    let mut arr_index = 0;

    // the first iteration is an empty bet, so we skip it with skip(1)
    for (a, b, c, d, e) in iproduct!(0..5, 0..5, 0..5, 0..5, 0..5).skip(1) {
        let mut total_bin: u32 = 0;
        let mut total_stds: f64 = 1.0;
        let mut total_odds: u32 = 1;

        let nums = vec![a, b, c, d, e];
        for (arena, index) in nums.iter().enumerate() {
            if *index == 0 {
                continue;
            }
            total_bin += 1 << (19 - (index - 1 + arena * 4));
            total_stds *= stds[arena][*index];
            total_odds *= odds[arena][*index];
        }

        _bins[arr_index] = total_bin;
        _stds[arr_index] = total_stds;
        _odds[arr_index] = total_odds;
        _ers[arr_index] = total_stds * total_odds as f64;
        _maxbets[arr_index] = (1_000_000.0 / total_odds as f64).ceil() as u32;

        arr_index += 1;
    }

    (
        _bins.to_pyarray(py),
        _stds.to_pyarray(py),
        _odds.to_pyarray(py),
        _ers.to_pyarray(py),
        _maxbets.to_pyarray(py),
    )
}

#[pyfunction]
fn build_chance_objects(
    bets: Vec<Vec<u8>>,
    bet_odds: Vec<u32>,
    probabilities: [[f64; 5]; 5],
) -> Vec<Chance> {
    let expanded = expand_ib_object(bets, bet_odds);

    let mut win_table: BTreeMap<u32, f64> = BTreeMap::new();
    for (key, value) in expanded.iter() {
        *win_table.entry(*value).or_insert(0.0) += ib_prob(*key, probabilities);
    }

    let mut cumulative: f64 = 0.0;
    let mut tail: f64 = 1.0;
    let mut chances: Vec<Chance> = Vec::new();
    for (key, value) in win_table.into_iter() {
        cumulative += value;

        chances.push(Chance {
            value: key,
            probability: value,
            cumulative,
            tail,
        });

        tail -= value;
    }
    chances
}

#[pymodule]
#[pyo3(name = "neofoodclub")]
fn neofoodclub_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(amounts_hash_to_bet_amounts, m)?)?;
    m.add_function(wrap_pyfunction!(bet_amounts_to_amounts_hash, m)?)?;
    m.add_function(wrap_pyfunction!(bets_hash_to_bet_binaries, m)?)?;
    m.add_function(wrap_pyfunction!(bets_hash_to_bet_indices, m)?)?;
    m.add_function(wrap_pyfunction!(bets_hash_to_bets_count, m)?)?;
    m.add_function(wrap_pyfunction!(bets_hash_value, m)?)?;
    m.add_function(wrap_pyfunction!(bets_indices_to_bet_binaries, m)?)?;
    m.add_function(wrap_pyfunction!(binary_to_indices, m)?)?;
    m.add_function(wrap_pyfunction!(build_chance_objects, m)?)?;
    m.add_function(wrap_pyfunction!(make_probabilities, m)?)?;
    m.add_function(wrap_pyfunction!(make_round_dicts, m)?)?;
    m.add_function(wrap_pyfunction!(pirate_binary, m)?)?;
    m.add_function(wrap_pyfunction!(pirates_binary, m)?)?;
    m.add("BET_AMOUNT_MAX", BET_AMOUNT_MAX)?;
    m.add("BET_AMOUNT_MIN", BET_AMOUNT_MIN)?;
    m.add("BIT_MASKS", BIT_MASKS)?;
    Ok(())
}
