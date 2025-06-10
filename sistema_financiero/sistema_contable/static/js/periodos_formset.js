document.addEventListener('DOMContentLoaded', function() {
    const table = document.getElementById('periodosTable').getElementsByTagName('tbody')[0];
    const addBtn = document.getElementById('agregarPeriodo');
    const totalForms = document.getElementById('id_form-TOTAL_FORMS');

    addBtn.addEventListener('click', function() {
        const currentFormCount = parseInt(totalForms.value);
        const newForm = table.querySelector('tr.periodo-form').cloneNode(true);

        // Limpiar los valores de los inputs clonados
        newForm.querySelectorAll('input').forEach(function(input) {
            if (input.type === 'checkbox') {
                input.checked = false;
            } else {
                input.value = '';
            }
            // Actualizar los atributos name y id
            input.name = input.name.replace(/-\d+-/, `-${currentFormCount}-`);
            input.id = input.id.replace(/-\d+-/, `-${currentFormCount}-`);
        });

        table.appendChild(newForm);
        totalForms.value = currentFormCount + 1;
    });

    // Eliminar fila
    table.addEventListener('click', function(e) {
        if (e.target.classList.contains('eliminar-fila')) {
            const rows = table.querySelectorAll('tr.periodo-form');
            if (rows.length > 1) {
                e.target.closest('tr').remove();
                totalForms.value = rows.length - 1;
            }
        }
    });
});