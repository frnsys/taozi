let toastsEl;
function toast(message, timeout) {
  if (!toastsEl) {
    toastsEl = document.createElement('div');
    toastsEl.id = 'toasts';
    document.body.appendChild(toastsEl);
  }

  let el = document.createElement('div');
  el.classList.add('toast');
  el.innerText = message;
  toastsEl.insertBefore(el, toastsEl.firstChild);

  if (timeout) {
    setTimeout(() => {
      toastsEl.removeChild(el);
    }, timeout);
  }
}

// https://gist.github.com/codeguy/6684588#gistcomment-3243980
function slugify(text) {
  return text
    .toString()                     // Cast to string
    .toLowerCase()                  // Convert the string to lowercase letters
    .normalize('NFD')               // The normalize() method returns the Unicode Normalization Form of a given string.
    .trim()                         // Remove whitespace from both sides of a string
    .replace(/\s+/g, '-')           // Replace spaces with -
    .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
    .replace(/\-\-+/g, '-');        // Replace multiple - with single -
}

function formatDate(d) {
  let month = (d.getMonth() + 1).toString().padStart(2, '0');
  let day = d.getDate().toString().padStart(2, '0');
  let hours = d.getHours().toString().padStart(2, '0');
  let mins = d.getMinutes().toString().padStart(2, '0');
  return `${d.getFullYear()}-${month}-${day} ${hours}:${mins}`;
}

const api = {
  post: async (endpoint, formData, csrfToken) => {
    let data = new FormData();
    Object.keys(formData).forEach((k) => {
      data.append(k, formData[k]);
    });
    let res = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'X-CSRF-Token': csrfToken,
          'Accept': 'application/json',
        },
        body: data
    });
    return await res.json();
  },

  del: async (endpoint) => {
    let res = await fetch(endpoint, {
        method: 'DELETE',
    });
    return await res.json();
  }
}

function $(sel) {
  return document.querySelector(sel);
}

function setStyle(el, style) {
  Object.keys(style).forEach((k) => {
    el.style[k] = style[k];
  });
}

function el(spec) {
  let pa = document.createElement(spec.tag);
  let children = spec.children || [];
  delete spec.tag;
  delete spec.children;

  let events = spec.on || {};
  Object.keys(events).forEach((ev) => {
    pa.addEventListener(ev, events[ev]);
  });
  delete spec.on;

  let dataset = spec.dataset || {};
  Object.keys(dataset).forEach((k) => {
    pa.dataset[k] = dataset[k];
  });
  delete spec.dataset;

  Object.keys(spec).forEach((k) => {
    pa[k] = spec[k];
  });

  children.forEach((ch) => {
    let e = ch instanceof HTMLElement ? ch : el(ch);
    pa.appendChild(e);
  });
  return pa;
}
