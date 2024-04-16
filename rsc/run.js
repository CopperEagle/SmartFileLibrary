async function displayResults() {
    const queryInput = document.getElementById('query-input').value;
    const typeInput = document.getElementById('form-dropdown').value;    

    // Sample data for demonstration
    const response = await fetch("http://localhost:5000/query?kw="+queryInput+"&t="+typeInput);
    const sampleData = await response.json();
    const resultsContainer = document.getElementById('results-container');
    resultsContainer.innerHTML = ''; // Clear previous results

    sampleData.forEach(entry => {
        const resultEntry = document.createElement('div');
        resultEntry.className = 'result-entry';
                
                            
        resultEntry.innerHTML = `
            <div class="entry-left">
                <div class="entry-title">${entry.title}</div>
                <div class="entry-author">${entry.author}</div>
            </div>
            <div class="entry-keywords">
                ${entry.keywords.map(keyword => `<span class="keyword">${keyword}</span>`).join(' ')}
            </div>
            <span class="${entry.favourite ? 'fav-star' : 'non-fav-star'}" onclick="toggleFavourite(this)">${entry.favourite ? '⭐' : '☆'}</span>
        `;
         // Calculate keywordBasis for each entry
        const containerWidth = resultsContainer.offsetWidth;
        const titleElement = resultEntry.querySelector('.entry-left');
        const titleWidth = titleElement.offsetWidth;
        const keywordBasis = 100 - (containerWidth - titleWidth)/containerWidth;// - 200; // Adjust as needed
                
        // Set keywordBasis for this entry
        resultEntry.style.setProperty('--keyword-basis', `${keywordBasis}%`);
   
        resultsContainer.appendChild(resultEntry);
    });
}
        
function toggleFavourite(starElement) {
    starElement.classList.toggle('fav-star');
    starElement.classList.toggle('non-fav-star');
    starElement.innerHTML = starElement.classList.contains('fav-star') ? '⭐' : '☆';
}

async function inputPressEnter(event) {
    if (event.key == "Enter") {
        displayResults()
    }
}