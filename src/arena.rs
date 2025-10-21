use pyo3::prelude::*;

#[pyclass]
#[derive(Clone)]
pub struct Arena {
    pub inner: neofoodclub::arena::Arena,
}

impl From<neofoodclub::arena::Arena> for Arena {
    fn from(arena: neofoodclub::arena::Arena) -> Self {
        Arena { inner: arena }
    }
}

#[pymethods]
impl Arena {
    #[getter]
    fn name(&self) -> &'static str {
        self.inner.get_name()
    }

    #[getter]
    fn winner_index(&self) -> u8 {
        self.inner.winner
    }

    #[getter]
    fn winner_pirate(&self) -> Option<crate::pirates::Pirate> {
        self.inner
            .pirates
            .get(self.inner.winner as usize - 1)
            .map(|p| crate::pirates::Pirate::from(*p))
    }

    #[getter]
    fn foods<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, pyo3::types::PyTuple>>> {
        match self.inner.foods {
            Some(f) => Ok(Some(pyo3::types::PyTuple::new(py, f)?)),
            None => Ok(None),
        }
    }

    #[getter]
    fn is_positive(&self) -> bool {
        self.inner.is_positive()
    }

    #[getter]
    fn is_negative(&self) -> bool {
        self.inner.is_negative()
    }

    #[getter]
    fn best(&self) -> Vec<crate::pirates::Pirate> {
        self.inner
            .best()
            .into_iter()
            .map(crate::pirates::Pirate::from)
            .collect()
    }

    #[getter]
    fn pirate_ids<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, pyo3::types::PyTuple>> {
        pyo3::types::PyTuple::new(py, self.inner.ids())
    }

    #[getter]
    fn ratio(&self) -> f64 {
        self.inner.ratio()
    }

    #[getter]
    fn id(&self) -> u8 {
        self.inner.id
    }

    #[getter]
    fn pirates(&self) -> Vec<crate::pirates::Pirate> {
        self.inner
            .pirates
            .iter()
            .map(|p| crate::pirates::Pirate::from(*p))
            .collect()
    }

    #[getter]
    fn odds(&self) -> f64 {
        self.inner.odds
    }

    fn __getitem__(&self, index: u8) -> PyResult<crate::pirates::Pirate> {
        let pirate = self.inner.get_pirate_by_index(index).ok_or_else(|| {
            pyo3::exceptions::PyIndexError::new_err(format!("list index out of range: {}", index))
        })?;
        Ok(crate::pirates::Pirate::from(*pirate))
    }

    fn __repr__(&self) -> String {
        format!(
            "<Arena name={:?} odds={:?} pirates={:?}>",
            self.name(),
            self.odds(),
            self.inner.pirates
        )
    }
}

#[pyclass]
pub struct Arenas {
    inner: neofoodclub::arena::Arenas,
}

impl From<neofoodclub::arena::Arenas> for Arenas {
    fn from(arenas: neofoodclub::arena::Arenas) -> Self {
        Arenas { inner: arenas }
    }
}

#[pymethods]
impl Arenas {
    #[getter]
    fn arenas(&self) -> Vec<Arena> {
        self.inner
            .arenas
            .iter()
            .map(|a| Arena::from(a.clone()))
            .collect()
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyResult<Py<ArenaIterator>> {
        let iter = ArenaIterator {
            arenas: slf.arenas().into_iter(),
        };
        Py::new(slf.py(), iter)
    }

    fn get_pirate_by_id(&self, id: u8) -> Option<crate::pirates::Pirate> {
        self.inner
            .get_pirate_by_id(id)
            .map(crate::pirates::Pirate::from)
    }

    fn get_pirates_by_id(&self, ids: Vec<u8>) -> Vec<crate::pirates::Pirate> {
        self.inner
            .get_pirates_by_id(&ids)
            .into_iter()
            .map(crate::pirates::Pirate::from)
            .collect()
    }

    fn get_all_pirates_flat(&self) -> Vec<crate::pirates::Pirate> {
        self.inner
            .get_all_pirates_flat()
            .iter()
            .map(|p| crate::pirates::Pirate::from(**p))
            .collect()
    }

    fn get_pirates_from_binary(&self, binary: u32) -> Vec<crate::pirates::Pirate> {
        self.inner
            .get_pirates_from_binary(binary)
            .into_iter()
            .map(crate::pirates::Pirate::from)
            .collect()
    }

    fn get_all_pirates(&self) -> Vec<Vec<crate::pirates::Pirate>> {
        self.inner
            .get_all_pirates()
            .into_iter()
            .map(|p| p.into_iter().map(crate::pirates::Pirate::from).collect())
            .collect()
    }

    #[getter]
    fn best(&self) -> Vec<Arena> {
        self.inner
            .best()
            .iter()
            .map(|a| Arena::from(a.clone()))
            .collect()
    }

    #[getter]
    fn pirate_ids<'py>(&self, py: Python<'py>) -> PyResult<Vec<Bound<'py, pyo3::types::PyTuple>>> {
        self.inner
            .arenas
            .iter()
            .map(|a| pyo3::types::PyTuple::new(py, a.ids()))
            .collect()
    }

    #[getter]
    fn positives(&self) -> Vec<Arena> {
        self.inner
            .positives()
            .iter()
            .map(|&a| Arena::from(a.clone()))
            .collect()
    }

    fn get_arena(&self, id: usize) -> PyResult<Arena> {
        let arena = self.inner.get_arena(id).ok_or_else(|| {
            pyo3::exceptions::PyIndexError::new_err(format!("list index out of range: {}", id))
        })?;
        Ok(Arena::from(arena.clone()))
    }

    fn __getitem__(&self, id: usize) -> PyResult<Arena> {
        let arena = self.inner.get_arena(id).ok_or_else(|| {
            pyo3::exceptions::PyIndexError::new_err(format!("list index out of range: {}", id))
        })?;
        Ok(Arena::from(arena.clone()))
    }

    fn __repr__(&self) -> String {
        format!("<Arenas {:?}>", self.inner.arenas)
    }

    fn __len__(&self) -> usize {
        5
    }
}
#[pyclass]
struct ArenaIterator {
    arenas: std::vec::IntoIter<Arena>,
}

#[pymethods]
impl ArenaIterator {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<'_, Self>) -> Option<Arena> {
        slf.arenas.next()
    }
}
