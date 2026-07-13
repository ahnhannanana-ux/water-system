window.addEventListener("load", () => {

    //----------------------------------
    // Progress Ring
    //----------------------------------

    const circle = document.getElementById("progressCircle");

    if(circle){

        const radius = 100;

        const circumference = 2 * Math.PI * radius;

        circle.style.strokeDasharray = circumference;

        circle.style.strokeDashoffset = circumference;

        const percent = Number(
            document.getElementById("progressBar").dataset.percent
        );

        if(percent<=50){
            circle.classList.add("red-ring");
        }

        else if(percent<=70){

            circle.classList.add("yellow-ring");
        }

        else{

           circle.classList.add("green-ring");

        }

        let current = 0;

        const timer = setInterval(()=>{

            current++;

            if(current>percent){

                clearInterval(timer);

            }

            const offset =
                circumference -
                current/100*circumference;

            circle.style.strokeDashoffset = offset;

        },15);

    }

    //----------------------------------
    // Progress Bar
    //----------------------------------

    const bar = document.getElementById("progressBar");

    if(bar){

        const percent = bar.dataset.percent;

        setTimeout(()=>{

            bar.style.width = percent+"%";

        },300);

    }

    //----------------------------------
    // Card Animation
    //----------------------------------

    const cards=document.querySelectorAll(".card");

    cards.forEach((card,index)=>{

        card.style.opacity="0";

        card.style.transform="translateY(40px)";

        setTimeout(()=>{

            card.style.transition=".6s";

            card.style.opacity="1";

            card.style.transform="translateY(0px)";

        },index*180);

    });

});