// Script to integrate the web scraping backend with the ShopSmart frontend
// This would be placed in a separate JavaScript file linked to your HTML

document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const searchInput = document.querySelector('.search-input');
    const searchButton = document.querySelector('.search-button');
    const productsGrid = document.querySelector('.products-grid');
    const resultsCount = document.querySelector('.results-count');
    
    // Add event listener to search button
    searchButton.addEventListener('click', function() {
        const searchQuery = searchInput.value.trim();
        
        if (searchQuery) {
            // Show loading state
            productsGrid.innerHTML = '<div class="loading">Searching across platforms...</div>';
            resultsCount.textContent = 'Searching...';
            
            // Call the backend API to get scraping results
            fetchProductResults(searchQuery);
        }
    });
    
    // Also trigger search on Enter key
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchButton.click();
        }
    });
    
    // Function to fetch results from the backend API
    function fetchProductResults(query) {
        // In a real implementation, this would call your backend API
        // Here we're simulating a backend call with a timeout
        
        // For actual implementation, you would use fetch:
        /*
        fetch(`/api/search?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                displayResults(data, query);
            })
            .catch(error => {
                console.error('Error fetching results:', error);
                productsGrid.innerHTML = '<div class="error">Error searching for products. Please try again.</div>';
            });
        */
        
        // Simulation for demonstration
        setTimeout(() => {
            // This would be the data returned from your Python backend
            const mockData = generateMockResults(query);
            displayResults(mockData, query);
        }, 1500); // Simulate network delay
    }
    
    // Function to display results on the page
    function displayResults(data, query) {
        // Clear previous results
        productsGrid.innerHTML = '';
        
        // Update results count
        const totalResults = data.length;
        resultsCount.textContent = `${totalResults} results for "${query}"`;
        
        if (totalResults === 0) {
            productsGrid.innerHTML = '<div class="no-results">No products found. Try a different search term.</div>';
            return;
        }
        
        // Group results by source
        const amazonResults = data.filter(item => item.source === 'Amazon');
        const flipkartResults = data.filter(item => item.source === 'Flipkart');
        
        // Render Amazon results
        amazonResults.forEach(product => {
            const productCard = createProductCard(product);
            productsGrid.appendChild(productCard);
        });
        
        // Render Flipkart results
        flipkartResults.forEach(product => {
            const productCard = createProductCard(product);
            productsGrid.appendChild(productCard);
        });
    }
    
    // Helper function to create a product card
    function createProductCard(product) {
        const card = document.createElement('div');
        card.className = 'product-card';
        
        // Add source badge (Amazon or Flipkart)
        const sourceBadge = document.createElement('div');
        sourceBadge.className = 'source-badge';
        sourceBadge.textContent = product.source;
        sourceBadge.style.position = 'absolute';
        sourceBadge.style.top = '10px';
        sourceBadge.style.right = '10px';
        sourceBadge.style.backgroundColor = product.source === 'Amazon' ? '#ff9900' : '#2874f0';
        sourceBadge.style.color = 'white';
        sourceBadge.style.padding = '3px 8px';
        sourceBadge.style.borderRadius = '3px';
        sourceBadge.style.fontSize = '12px';
        
        card.innerHTML = `
            <div style="position: relative;">
                <img src="${product.image_url || '/api/placeholder/400/320'}" alt="${product.title}" class="product-image">
            </div>
            <div class="product-info">
                <h3 class="product-title">${product.title}</h3>
                <div class="product-price">${product.price}</div>
                <div class="product-rating">${product.rating}</div>
                <a href="${product.url}" target="_blank" class="add-to-cart" style="display: block; text-align: center; text-decoration: none;">
                    View on ${product.source}
                </a>
            </div>
        `;
        
        card.querySelector('div[style="position: relative;"]').appendChild(sourceBadge);
        
        return card;
    }
    
    // For demonstration purposes - generate mock results
    // In a real implementation, this data would come from your backend
    function generateMockResults(query) {
        // Simulate results based on query
        const results = [];
        
        // Amazon results
        for (let i = 1; i <= 5; i++) {
            results.push({
                title: `Amazon ${query} - Model ${i}`,
                price: `$${Math.floor(Math.random() * 500) + 100}.99`,
                rating: `${(Math.random() * 2 + 3).toFixed(1)} stars (${Math.floor(Math.random() * 1000)})`,
                url: 'https://www.amazon.com',
                image_url: '/api/placeholder/400/320',
                source: 'Amazon'
            });
        }
        
        // Flipkart results
        for (let i = 1; i <= 5; i++) {
            results.push({
                title: `Flipkart ${query} - Model ${i}`,
                price: `₹${Math.floor(Math.random() * 40000) + 10000}`,
                rating: `${(Math.random() * 2 + 3).toFixed(1)} stars (${Math.floor(Math.random() * 1000)})`,
                url: 'https://www.flipkart.com',
                image_url: '/api/placeholder/400/320',
                source: 'Flipkart'
            });
        }
        
        return results;
    }
});
