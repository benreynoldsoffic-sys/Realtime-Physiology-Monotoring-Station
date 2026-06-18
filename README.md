# Realtime Physiology Monotoring Station <br> [Table of Contents]
- [Section 1: Introduction and Learning Resources](#section-1-introduction-and-learning-resources)
  - [1.a — Welcome to the Project](#1a--welcome-to-the-project)
  - [1.b — Current Abilities of the Program and Recommendations for Use Cases](#1b--current-abilities-of-the-program-and-recommendations-for-use-cases)
  - [1.c — Learning and Resources](#1c--learning-and-resources)
- [Section 2: Set Up and Development](#section-2-set-up-and-development)
  - [2.a — Step-by-Step Setup for Windows](#2a--step-by-step-setup-for-windows)
  - [2.b — Development Functions: Incoming Data](#2b--development-functions-incoming-data)
  - [2.c — Development Functions: Data Analysis](#2c--development-functions-data-analysis)
---

## Section 1: Introduction and Learning Resources

---

### 1.a — Welcome to the Project

While codebases like ROS2 are an excelent foundation for developing realtime systems, these codebases are focused on enebaling as many kinds of hardware, data speeds, and encoding styles as possible. So while it can be reworked to transfer information amongst more complex data colection devices this can pose a time constraint having to learn the whole system and work within its existing constraints, which may be unfesable for some labritorys and reserch institutions. Lead to the creation of the RPMS (Realtime Physiology Monotering System), developed as a more focused framework from which realtime human physiological data may be taken in, cleaned, and analysed, producing more complex features at a semi realtime rate. That said, it is not limited to human physiology alone. This system simply provides a foundation upon which any incoming live data can be extracted and examined in a quasi-real-time fashion.

I would like to take a moment to note that this project likely has some bugs that I have missed, for this reason I have included as many resources as possible inorder to show you my thought process in its development and aid in the debuging process.

This project was last updated:

\[06/18/2026]

---

### 1.b — Current Abilities of the Program and Recommendations for Use Cases

System requires that the following be true of any device (or associated device software) used in the collection of incoming data:
- Be able to generate consistant data packages; i.e. the data packet will mantain a specefied length and structure like [ [x, y, voltage, strain, time] , [x, y, voltage, strain, time] ].
- Be able to conect and transmit to an existing TCP conection.
- If unable to transmit via TCP conection itself be able to ECHO the data.
- Be able to send data reliably and on a consistant schedule.

System requires the following hardware to be true of any device atempting to run this system:
- Enough ports to conect your devices too. 
- 16 CPU cores
- 16 GB of RAM

With regard to the systems current abilitys there are 2 factors to keep in mind: First the number of CPU Cores avalable on the device atempting to run this system, I have done my best to limit the possible number of context switches

---

### 1.c — Learning and Resources

There are three key design spaces you as a developer must concider when incorperating this project with your own existing methodology. First, where will the data be coming from; in the supporting resources bellow I have used the BIOPAC family of products as an example of products that you yourself may be using and what kind of information we want about that product inorder to properly and routinely get information passed from one source to another. Second, is multi procesing, which may seem strange. However, most reserchers who have only ever used Matlab or Rstudio may require aditional help understanding how exactly they need to break apart their existing system inorder to truly use this system to its fullest potential. Third, Python, while an advanced understanding of python is not required there is some strangeness to the way the system has been designed and mostly due to the python coding languages. All of these are not required readings but they are encoraged if you ever find yourself confused on a topic or getting an unforseen result, aside from emailing me these should at the very least point you in the right direction.

| Resource Type | Biopac | Multi-Processing | Python |
|----------------|--------|-----------------|--------|
| **Basic**   | wondering what kind of resources you are even looking for? [Click Me](https://www.biopac.com/product/mp200-systems-with-ndt/) | Confused on multiprocesing as a whole? [Click Me]( https://www.geeksforgeeks.org/operating-systems/multi-processing-operating-system/) | Objects not working?  [Click Me](https://www.geeksforgeeks.org/python/python-oops-concepts/)|
| **Complex**| Confused on converting coe? [Click Me](https://tristan-ka.github.io/IBOAT_RL/_downloads/SIMULINK_TO_C__PYTHON.pdf) | Quis nostrud exercitation | Ullamco laboris nisi |
| **Advanced**   | Duis aute irure dolor | Reprehenderit in voluptate | Velit esse cillum dolore |


**Basic:** A basic resource is a lower complexity resource that should ether help give an example of where why or how common problems or misunderstandings may occure.


**Complex** A complex resource is more specific but still can be the result of a misunderstanding between an explination here and the exicution.

---

## Section 2: Set Up and Development
<p align="center">
  <img src="./Supp_Images/Git edit Collector system cycles.png" alt="Project Overview 3" width="600%"/>
</p>

<br>

<p align="center">
  <img src="./Supp_Images/Git edit Collector system cycles.png" alt="Project Overview 3" width="600"/>
</p>

---

### 2.a — Step-by-Step Setup for Windows

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Follow the steps below in order to download and configure the system on a Windows machine. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

---

**Step 1 — [Step Title]**

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

<p align="center">
  <img src="./assets/images/setup/step_1.png" alt="Step 1" width="600"/>
</p>

---

**Step 2 — [Step Title]**

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

<p align="center">
  <img src="./assets/images/setup/step_2.png" alt="Step 2" width="600"/>
</p>

---

**Step 3 — [Step Title]**

Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam. Eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit.

<p align="center">
  <img src="./assets/images/setup/step_3.png" alt="Step 3" width="600"/>
</p>

---

**Step 4 — [Step Title]**

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.

<p align="center">
  <img src="./assets/images/setup/step_4.png" alt="Step 4" width="600"/>
</p>

---

**Step 5 — [Step Title]**

Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium. Totam rem aperiam eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.

<p align="center">
  <img src="./assets/images/setup/step_5.png" alt="Step 5" width="600"/>
</p>

---

### 2.b — Development Functions: Incoming Data

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.

<p align="center">
  <img src="./assets/images/dev/incoming_1.png" alt="Incoming Data Function Example" width="600"/>
</p>

At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident. Similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga.

<p align="center">
  <img src="./assets/images/dev/incoming_2.png" alt="Incoming Data Function Example 2" width="600"/>
</p>

Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet.

---

### 2.c — Development Functions: Data Analysis

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.

<p align="center">
  <img src="./assets/images/dev/analysis_1.png" alt="Analysis Function Example" width="600"/>
</p>

At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident. Similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio.

<p align="center">
  <img src="./assets/images/dev/analysis_2.png" alt="Analysis Function Example 2" width="600"/>
</p>

Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae.

---
