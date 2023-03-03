const searchForm = document.querySelector('.search-form');

searchForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const searchInput = document.querySelector('.search-form__input');
  const searchTerm = searchInput.value;
  const url = `/movies?title=${searchTerm}`;

  fetch(url)
    .then(response => response.text())
    .then(data => {
      const movieList = document.querySelector('.movie-list');
      movieList.innerHTML = data;
    })
    .catch(error => console.log(error));
});
