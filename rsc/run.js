
        Vue.component('resultentry', {
            props: ['entry', 'favourites'],
            template: `
                <div class="result-entry" @click="displayPopup">
                    <div class="entry-left">
                        <div class="entry-title">{{ entry.title }}</div>
                        <div class="entry-author">{{ entry.author }}</div>
                    </div>
                    <div class="entry-keywords">
                        <span v-for="keyword in entry.keywords" class="keyword">{{ keyword }}</span>
                    </div>
                    <span @click.stop="toggleFavourite" :class="{ 'fav-star': isFavourite, 'non-fav-star': !isFavourite }">{{ isFavourite ? '⭐' : '☆' }}</span>
                </div>
            `,
            computed: {
                isFavourite() {
                    return this.favourites.includes(this.entry.id);
                }
            },
            mounted() {
            	const containerWidth = this.$el.offsetWidth;
                const titleElement = this.$el.querySelector('.entry-left');
                const titleWidth = titleElement.offsetWidth;
                const keywordBasis = 100 - (containerWidth - titleWidth) / containerWidth; // Adjust as needed
                // Set keywordBasis for this entry
                this.$el.style.setProperty('--keyword-basis', `${keywordBasis}%`);
                if (this.entry.favourite){
                	this.favourites.push(this.entry.id);
                }
            
            },
            methods: {
                toggleFavourite() {
                    this.$emit('toggle-favourite', this.entry);
                },
                displayPopup() {
                    this.$emit('display-popup', this.entry);
                }
            }
        });

        const app = new Vue({
            el: '#app',
            data: {
                query: '',
                type: 'all',
                results: [],
                popupVisible: false,
                popupContent: {
                    title: '',
                    author: '',
                    keywords: []
                },
                favourites: []
            },
            methods: {
                displayResults() {
                    const queryUrl = `http://localhost:5000/query?kw=${encodeURIComponent(this.query)}&form=${this.type}`;
                    fetch(queryUrl)
                        .then(response => response.json())
                        .then(data => {
                            this.results = data;
                        })
                        .catch(error => {
                            console.error('Error fetching data:', error);
                        });
                },
                toggleFavourite(entry) {
                    const index = this.favourites.indexOf(entry.id);
                    if (index !== -1) {
                        this.favourites.splice(index, 1);
                        const queryUrl = `http://localhost:5000/set_fav?id=${entry.id}&val=0`;
                    	fetch(queryUrl);
                    } else {
                        this.favourites.push(entry.id);
                        const queryUrl = `http://localhost:5000/set_fav?id=${entry.id}&val=1`;
                    	fetch(queryUrl);
                    }
                },
                displayPopup(entry) {
                    
                    this.popupContent = entry;
                    this.popupVisible = true;
                },
                hidePopup() {
                    this.popupVisible = false;
                }
            }
        });

