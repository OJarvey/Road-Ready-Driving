window.onscroll = function () { scrollFunction() };

function scrollFunction() {
  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
    document.querySelector(".btt-button").style.display = "block";
  } else {
    document.querySelector(".btt-button").style.display = "none";
  }
}

document.querySelector('.btt-button').addEventListener('click', function () {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});
