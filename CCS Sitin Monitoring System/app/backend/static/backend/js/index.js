function RenderErrorDiv(parentElement, data) {
    for (let field in data) {
        let errorDiv = document.createElement('div');
        errorDiv.classList.add('alert', 'alert-danger', 'mb-1', 'small');
        errorDiv.textContent = `${field.toUpperCase()}: ${data[field].join(", ")}`;
        parentElement.insertAdjacentElement("beforebegin", errorDiv);
    }
}