
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
                        .then(response => {
                            if (response.status_code >= 500){
                                setStatusError();
                            } else if (response.status_code >= 400){
                                setStatusClientError();
                            };
                            return response.json();

                        })
                        .then(data => {
                            setStatusRunning();
                            this.results = data;
                        })
                        .catch(error => {
                            console.error('Error fetching data:', error);
                            setStatusOffline();
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


        // JavaScript functions to set the status
        function _resetServerStatus() {
            const elt = document.getElementById("status-circle-id");
            elt.classList.remove("status-offline");
            elt.classList.remove("status-error");
            elt.classList.remove("status-running");
        }

        function _updateStatusDisclaimer(colorcls, text){
            document.getElementById("status-circle-id").classList.add(colorcls);
            document.getElementById("status-disclaimer-text").innerHTML = text;
        }

        function setStatusRunning() {
            _resetServerStatus();
            _updateStatusDisclaimer("status-running", "Server running");
        }

        function setStatusOffline() {
            _resetServerStatus();
            _updateStatusDisclaimer("status-offline", "Server offline");
        }

        function setStatusError() {
            _resetServerStatus();
            _updateStatusDisclaimer("status-error", "Server error");
        }

        function setStatusClientError() {
            _resetServerStatus();
            _updateStatusDisclaimer("status-error", "Client error");
        }

        function access_resource(queryUrl){
            var network_works = false;
            return fetch(queryUrl)
                .then(response => {
                    if (response.status >= 500){
                        network_works = true;
                        setStatusError();
                        return null;
                    } else if (response.status >= 400){
                        network_works = true;
                        setStatusClientError();
                        return null;
                    } else {
                        setStatusRunning();
                    }
                    return response.json()
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                    if (!network_works){
                        setStatusOffline();
                    }
                    return null;
                });
            
        }

        function checkServerStatus(){
            const queryUrl = `http://localhost:5000/status`;
            access_resource(queryUrl);
            
        }

        function getUserName(){
            const queryUrl = `http://localhost:5000/dbmeta?key=user`;
            var promise = access_resource(queryUrl);
            promise.then(username => {
                if (username == null){
                    username = "Username could not be loaded...";
                }
                document.getElementById("user-name").innerHTML = username;
            });
        }

        function sendServerOff(){
            const queryUrl = `http://localhost:5000/turnoff`;
            access_resource(queryUrl);
        }

        function doswitch(){
            const elt = document.getElementById("menubuttonid");
            elt.click();
        }

        function setMetadataModel(i){
            const elt = document.getElementById(`metadata-usage-field-${i}`);
            elt.innerHTML = "✅ &ensp;";
            var j = 1;
            while (true){
                try{
                    if (i == j){
                        j++;
                        continue;
                    }
                    const otherelt = document.getElementById(`metadata-usage-field-${j}`);
                    otherelt.innerHTML = " ";
                    j++;
                } catch{
                    break;
                }
            }
            
        }

