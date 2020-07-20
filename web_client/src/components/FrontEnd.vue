<template>
  <div class="login-box">
    <h2  v-if="step != 4">User Form</h2>
    <h2  v-if="step == 4">Thank you!</h2>

    <form id="app">
      <span style="color: red; font-weight: normal">{{ errors }}</span>
      <section v-if="step == 1">
        <h3>Please enter your email address</h3>

        <div class="user-box">
          <input
            v-model="form.email"
            type="email"
            placeholder="Email Address"
            class="form-control"
          />
        </div>
      </section>

      <section v-if="step == 2">
        <h3>Please enter your name</h3>
        <div class="user-box">
          <input
            v-model="form.name"
            type="text"
            placeholder="Name"
            class="form-control"
          />
        </div>
      </section>

      <section v-if="step == 3">
        <h3>Please enter your phone number</h3>
        <div class="user-box">
          <input
            v-model="form.phone"
            type="tel"
            placeholder="Phone number"
            class="form-control"
          />
        </div>
      </section>

      <button
        v-if="step != 1 && step != 4"
        @click.prevent="prevStep"
        class="btn-left"
      >
        Previous Step
      </button>
      <button
        v-if="step != totalsteps && step != 4"
        @click.prevent="nextStep"
        class="btn-right"
      >
        Next Step
      </button>
      <button
        v-if="step == 3 && step != 4"
        @click.prevent="sendEnquiry"
        class="btn-send"
      >
        Send Enquiry Step
      </button>
    </form>

    <div v-if="step == 4">
      <p>Email: {{ user.email }}</p>
      <p>Name: {{ user.name }}</p>
      <p>Phone: {{ user.phone }}</p>

      <button @click.prevent="reset" class="btn-reset">Reset</button>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "WebClient",
  data: function() {
    return {
      step: 1,
      totalsteps: 3,
      user: null,
      new_doc: null,
      errors: null,
      form: {
        email: null,
        name: null,
        phone: null,
      },
    };
  },
  methods: {
    prevStep: function() {
      this.errors = null;
      this.step--;
    },

    nextStep: function() {
      this.errors = null;
      if (this.step == 1) {
        if (!this.form.email) {
          this.errors = "Email address cannot be empty";
          return false;
        }
        if (!this.validEmail(this.form.email)) {
          this.errors = "Please enter a valid email address";
          return false;
        }
      }

      if (this.step == 2) {
        if (!this.form.name) {
          this.errors = "Name cannot be empty";
          return false;
        }

        if (!this.validName(this.form.name)) {
          this.errors = "Please enter a valid name";
          return false;
        }
      }

      this.step++;
    },

    sendEnquiry: function() {
      if (this.step == 3) {
        if (!this.form.phone) {
          this.errors = "Phone number cannot be empty";
          return false;
        }

        if (!this.validPhone(this.form.phone)) {
          this.errors = "Please enter a valid phone number";
          return false;
        }

        axios
          .post(`http://localhost:8085/doc/add`, {
            email: this.form.email,
            name: this.form.name,
            phone: this.form.phone,
          })
          .then((response) => {
            // JSON responses are automatically parsed.
            this.new_doc = response.data.id;

            axios
              .get(`http://localhost:8085/doc`, {
                params: { id: this.new_doc },
              })
              .then((response) => {
                // JSON responses are automatically parsed.
                this.user = response.data;
                this.step = 4;
              })
              .catch((e) => {
                this.errors.push(e);
              });
          })
          .catch((e) => {
            //this.errors.push(e);
            this.errors = e;
          });
      }
      this.errors = null;

    },
    reset: function() {
      this.step = 1;
      this.new_doc = null;
      this.user = null;
      this.form.email = null;
      this.form.name = null;
      this.form.phone = null;
    },
    validEmail: function(email) {
      var re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      return re.test(email);
    },
    validName: function(name) {
      var re = /^([A-Za-z'\s-]){2,32}$/;
      return re.test(name);
    },
    validPhone: function(phone) {
      var re = /^([+0-9]){10,15}$/;
      return re.test(phone);
    }
  },
  mounted() {},
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.login-box {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 400px;
  padding: 40px;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.5);
  box-sizing: border-box;
  box-shadow: 0 15px 25px rgba(0, 0, 0, 0.6);
  border-radius: 10px;
}

.login-box .user-box {
  position: relative;
}

.login-box .user-box {
  width: 100%;
  padding: 10px 0;
  font-size: 16px;
  color: #fff;
  margin-bottom: 30px;
  border: none;
  border-bottom: 1px solid #fff;
  outline: none;
  background: transparent;
}

.form-control {
  background: transparent;
  border: none;
}

::placeholder {
  color: #fff;
}

.btn-left {
  float: left;
  border: 3px solid rgb(12, 12, 12);
}

.btn-right {
  float: right;
  border: 3px solid rgb(12, 12, 12);
}

.btn-send {
  float: right;
  border: 3px solid rgb(14, 2, 78);
}

.btn-reset {
  float: right;
  border: 3px solid rgb(114, 5, 5);
}
</style>
