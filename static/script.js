

//first below

// document.getElementById('upload-form').addEventListener('submit', function (e) {
//     e.preventDefault();

//     const fileInput = document.getElementById('receipt');
//     const loading = document.getElementById('loading');
//     const resultContainer = document.getElementById('result');
//     const itemsList = document.getElementById('items-list');

//     const file = fileInput.files[0];
//     if (!file) {
//         alert('Please select a receipt image to upload.');
//         return;
//     }

//     const formData = new FormData();
//     formData.append('receipt', file);

//     // Show loading
//     loading.classList.remove('hidden');
//     resultContainer.classList.add('hidden');
//     itemsList.innerHTML = '';

//     fetch('/upload', {
//         method: 'POST',
//         body: formData
//     })
//     .then(res => res.json())
//     .then(data => {
//         loading.classList.add('hidden');
//         if (data.error) {
//             alert('Error: ' + data.error);
//             return;
//         }

//         if (data.items.length === 0) {
//             itemsList.innerHTML = '<li>No grocery items found.</li>';
//         } else {
//             data.items.forEach(item => {
//                 const li = document.createElement('li');
//                 li.textContent = item;
//                 itemsList.appendChild(li);
//             });
//         }

//         resultContainer.classList.remove('hidden');
//     })
//     .catch(error => {
//         loading.classList.add('hidden');
//         console.error('Upload failed:', error);
//         alert('Something went wrong. Please try again.');
//     });
// });


document.getElementById('upload-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const fileInput = document.getElementById('receipt');
    const loading = document.getElementById('loading');
    const resultContainer = document.getElementById('result');
    const itemsList = document.getElementById('items-list');
    const recommendationContainer = document.getElementById('recommendations');
    const recommendationList = document.getElementById('recommendation-list');

    const file = fileInput.files[0];
    if (!file) {
        alert('Please select a receipt image to upload.');
        return;
    }

    const formData = new FormData();
    formData.append('receipt', file);

    loading.classList.remove('hidden');
    resultContainer.classList.add('hidden');
    recommendationContainer.classList.add('hidden');
    itemsList.innerHTML = '';
    recommendationList.innerHTML = '';

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        loading.classList.add('hidden');

        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        data.items.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            itemsList.appendChild(li);
        });
        resultContainer.classList.remove('hidden');

        if (data.recommendations.length > 0) {
            data.recommendations.forEach(rec => {
                const li = document.createElement('li');
                li.textContent = rec;
                recommendationList.appendChild(li);
            });
            recommendationContainer.classList.remove('hidden');
        }
    })
    .catch(error => {
        loading.classList.add('hidden');
        alert('Something went wrong.');
        console.error(error);
    });
});
