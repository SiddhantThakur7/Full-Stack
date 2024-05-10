import firebase from "firebase/app";

import "firebase/firestore";
import "firebase/auth";

var firebaseConfig = {
  apiKey: "AIzaSyBb68LY77LaRP5HpDc_woCOcBqUNQLdhqY",
  authDomain: "crowndb-b05a0.firebaseapp.com",
  projectId: "crowndb-b05a0",
  storageBucket: "crowndb-b05a0.appspot.com",
  messagingSenderId: "866653539626",
  appId: "1:866653539626:web:171ca6fba2c6b228e1a253",
  measurementId: "G-DZGBZ4P6N2",
};

export const createUserProfileDocument = async (userAuth) => {
  if (!userAuth) {
    return;
  }
  const userRef = firestore.doc(`users/${userAuth.uid}`);
  const snapShot = await userRef.get();

  if(!snapShot.exists){
    const { displayName, email } = userAuth;
    const createdAt = new Date();

    try {
      await userRef.set({
        displayName,
        email, 
        createdAt
      })
    } catch (error) {
      console.log('error in creating user.', error.message);
    }
  }
  return userRef;
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);


export const addCollectionAndDocuments = async (collectionKey, objectsToAdd) => {
  const collectionRef = firestore.collection(collectionKey);
  console.log(collectionRef);

  const batch = firestore.batch();
  objectsToAdd.forEach(obj => {
    const newDocRef = collectionRef.doc();
    batch.set(newDocRef, obj);
  });

  return await batch.commit()
} 


export const convertCollectionsSnapshotToMap = collections => {
  const transformedCollection = collections.docs.map(doc => {
    const { title, items } = doc.data();

    return {
      routeName: encodeURI(title.toLowerCase()),
      id: doc.id,
      title,
      items
    };
  });

  return transformedCollection.reduce((accumulator, collection) => {
    accumulator[collection.title.toLowerCase()] = collection;
    return accumulator;
  }, {});
};


export const getCurrentUser = () => {
  return new Promise((resolve, reject) => {
    const unsubscribe = auth.onAuthStateChanged(userAuth => {
      unsubscribe();
      resolve(userAuth);
    }, reject)
  });
};


export const auth = firebase.auth();
export const firestore = firebase.firestore();

export const googleProvider = new firebase.auth.GoogleAuthProvider();
// const provider = new firebase.auth.GoogleAuthProvider();
// provider.setCustomParameters({ prompt: "select_account" });

export const signInWithGoogle = () => auth.signInWithPopup(googleProvider);

export default firebase;
