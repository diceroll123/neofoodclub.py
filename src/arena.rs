use pyo3::{prelude::*, types::PyTuple};

#[pyclass]
pub struct Arena {
    pub inner: neofoodclub::arena::Arena,
}

impl Arena {
    pub fn from_arena(arena: neofoodclub::arena::Arena) -> Self {
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
    fn winner(&self) -> u8 {
        self.inner.winner
    }

    #[getter]
    fn foods<'a>(&self, py: Python<'a>) -> PyResult<Option<&'a PyTuple>> {
        let elements = &self.inner.foods;

        match elements {
            Some(foods) => Ok(Some(PyTuple::new(py, foods))),
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
            .iter()
            .map(|p| crate::pirates::Pirate::from_pirate(*p))
            .collect()
    }

    #[getter]
    fn pirate_ids<'a>(&self, py: Python<'a>) -> PyResult<&'a PyTuple> {
        let elements = &self.inner.ids();
        Ok(PyTuple::new(py, elements))
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
            .map(|p| crate::pirates::Pirate::from_pirate(*p))
            .collect()
    }

    #[getter]
    fn odds(&self) -> f64 {
        self.inner.odds.clone()
    }

    fn __getitem__(&self, index: u8) -> crate::pirates::Pirate {
        let pirate = self
            .inner
            .get_pirate_by_index(index)
            .expect("list index out of range");
        crate::pirates::Pirate::from_pirate(*pirate)
    }
}

#[pyclass]
pub struct Arenas {
    inner: neofoodclub::arena::Arenas,
}

impl Arenas {
    pub fn from_arenas(arenas: neofoodclub::arena::Arenas) -> Self {
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
            .map(|a| Arena::from_arena(a.clone()))
            .collect()
    }

    fn get_pirate_by_id(&self, id: u8) -> Option<crate::pirates::Pirate> {
        self.inner
            .get_pirate_by_id(id)
            .map(|p| crate::pirates::Pirate::from_pirate(*p))
    }

    fn get_pirates_by_id(&self, ids: Vec<u8>) -> Vec<crate::pirates::Pirate> {
        self.inner
            .get_pirates_by_id(&ids)
            .iter()
            .map(|p| crate::pirates::Pirate::from_pirate(**p))
            .collect()
    }

    fn get_all_pirates_flat(&self) -> Vec<crate::pirates::Pirate> {
        self.inner
            .get_all_pirates_flat()
            .iter()
            .map(|p| crate::pirates::Pirate::from_pirate(**p))
            .collect()
    }

    fn get_pirates_from_binary(&self, binary: u32) -> Vec<crate::pirates::Pirate> {
        self.inner
            .get_pirates_from_binary(binary)
            .iter()
            .map(|p| crate::pirates::Pirate::from_pirate(**p))
            .collect()
    }

    fn get_all_pirates(&self) -> Vec<Vec<crate::pirates::Pirate>> {
        self.inner
            .get_all_pirates()
            .iter()
            .map(|p| {
                p.iter()
                    .map(|pirate| crate::pirates::Pirate::from_pirate(*pirate))
                    .collect()
            })
            .collect()
    }

    #[getter]
    fn best(&self) -> Vec<Arena> {
        self.inner
            .best()
            .iter()
            .map(|a| Arena::from_arena(a.clone()))
            .collect()
    }

    #[getter]
    fn pirate_ids<'a>(&self, py: Python<'a>) -> PyResult<&'a PyTuple> {
        let elements: Vec<&PyTuple> = self
            .arenas()
            .iter()
            .map(|a| a.pirate_ids(py).expect("failed to get pirate ids"))
            .collect();
        Ok(PyTuple::new(py, elements))
    }

    #[getter]
    fn positives(&self) -> Vec<Arena> {
        self.inner
            .positives()
            .iter()
            .map(|a| Arena::from_arena(a.clone()))
            .collect()
    }

    fn get_arena(&self, id: usize) -> Arena {
        let arena = self.inner.get_arena(id).expect("list index out of range");
        Arena::from_arena(arena.clone())
    }

    fn __getitem__(&self, id: usize) -> Arena {
        let arena = self.inner.get_arena(id).expect("list index out of range");
        Arena::from_arena(arena.clone())
    }
}