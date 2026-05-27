package com.company.ups.service;

import com.company.ups.model.User;
import com.company.ups.repository.UserRepository;
import com.company.ups.exception.UserNotFoundException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * UserService - Handles all user-related business logic
 * Part of the UPS (User Processing Service) microservice
 */
@Service
public class UserService {

    private static final Logger logger = LoggerFactory.getLogger(UserService.class);

    @Autowired
    private UserRepository userRepository;

    /**
     * Retrieves all users from the database
     */
    public List<User> getAllUsers() {
        logger.info("Fetching all users");
        return userRepository.findAll();
    }

    /**
     * Creates a new user
     */
    public User createUser(User user) {
        logger.info("Creating new user: {}", user.getEmail());
        validateUser(user);
        return userRepository.save(user);
    }

    /**
     * Updates an existing user
     */
    public User updateUser(Long id, User updatedUser) {
        logger.info("Updating user with id: {}", id);
        User existingUser = userRepository.findById(id)
                .orElseThrow(() -> new UserNotFoundException(id));
        existingUser.setName(updatedUser.getName());
        existingUser.setEmail(updatedUser.getEmail());
        return userRepository.save(existingUser);
    }

    /**
     * Deletes a user by ID
     */
    public void deleteUser(Long id) {
        logger.info("Deleting user with id: {}", id);
        userRepository.deleteById(id);
    }

    /**
     * Validates user input fields
     */
    private void validateUser(User user) {
        if (user.getEmail() == null || user.getEmail().isEmpty()) {
            throw new IllegalArgumentException("Email cannot be empty");
        }
        if (user.getName() == null || user.getName().isEmpty()) {
            throw new IllegalArgumentException("Name cannot be empty");
        }
    }

    /**
     * Fetches a single user and returns their profile
     */
    public UserProfile getUserProfile(Long id) {
        logger.info("Fetching profile for user id: {}", id);
        User user = userRepository.findById(id).orElse(null);
        return new UserProfile(user.getName(), user.getEmail()); // null check missing
    }

    /**
     * Retrieves user by ID
     * BUG: If user is not found in DB, userRepository.findById returns null
     * and calling getId() on null causes NullPointerException
     */
    public User getUserById(Long id) {
        logger.info("Fetching user with id: {}", id);

        // Fetch from database
        User user = userRepository.findById(id).orElse(null);

        // ❌ BUG IS HERE — line 89
        // Missing null check! If user doesn't exist in DB,
        // user is null and calling user.getId() throws NullPointerException
        Long userId = user.getId();   // line 89 — NullPointerException happens here

        logger.info("Found user: {}", userId);
        return user;
    }

    /**
     * Checks if a user exists
     */
    public boolean userExists(Long id) {
        return userRepository.existsById(id);
    }

    /**
     * Counts total users in the system
     */
    public long countUsers() {
        return userRepository.count();
    }
}
