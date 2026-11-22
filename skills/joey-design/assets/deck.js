(() => {
  const pages = [...document.querySelectorAll(".slide")];
  const previous = document.querySelector("#prev");
  const next = document.querySelector("#next");
  const counter = document.querySelector("output");
  const notes = document.querySelector("#notes");
  const panel = document.querySelector("#notes-panel");
  const notePages = [...panel.querySelectorAll("article")];
  function toggleNotes() {
    panel.hidden = !panel.hidden;
    notes.setAttribute("aria-expanded", String(!panel.hidden));
  }
  notes.onclick = toggleNotes;
  let index = 0;
  function show(i) {
    index = Math.max(0, Math.min(pages.length - 1, i));
    pages.forEach((page, n) => page.classList.toggle("active", n === index));
    notePages.forEach((page, n) => { page.hidden = n !== index; });
    previous.disabled = index === 0;
    next.disabled = index === pages.length - 1;
    counter.value = (index + 1) + " / " + pages.length;
  }
  previous.onclick = () => show(index - 1);
  next.onclick = () => show(index + 1);
  document.addEventListener("keydown", event => {
    if (!event.altKey && !event.ctrlKey && !event.metaKey && event.key.toLowerCase() === "n") {
      toggleNotes();
      return;
    }
    if (event.key === "Escape" && !panel.hidden) { toggleNotes(); return; }
    const keys = {ArrowRight:index+1, PageDown:index+1, ArrowLeft:index-1, PageUp:index-1, Home:0, End:pages.length-1};
    if (event.altKey || event.metaKey || event.ctrlKey || !(event.key in keys)) return;
    event.preventDefault();
    show(keys[event.key]);
  });
  pages.forEach((page, i) => { page.id = "slide-" + (i + 1); });
  function openHash() {
    const match = /^#slide-([1-9][0-9]*)$/.exec(location.hash);
    if (match) show(Number(match[1]) - 1);
    if (location.hash === "#notes-panel" && panel.hidden) toggleNotes();
  }
  document.addEventListener("click", event => {
    const link = event.target.closest("a.slide-action");
    if (link && link.hash && link.origin === location.origin && link.pathname === location.pathname &&
        link.hash === location.hash) openHash();
  });
  window.addEventListener("hashchange", openHash);
  show(0);
  openHash();
  document.documentElement.classList.add("ready");
})();
