// html/js tutorials about button from w3school https://www.w3schools.com/howto/howto_js_read_more.asp
function viewMoreOrLess(key) {
    let dotskey = "dots" + key;
    let morekey = "more" + key;
    let dots = document.getElementById(dotskey);
    let moreText = document.getElementById(morekey);
    let btnText = document.getElementById(key);

    if (dots.style.display === "none") {
        dots.style.display = "inline";
        btnText.innerHTML = "Read more";
        moreText.style.display = "none";
    } else {
        dots.style.display = "none";
        btnText.innerHTML = "Read less";
        moreText.style.display = "inline";
    }
}