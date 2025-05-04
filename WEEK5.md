# Week 5 Action Items
- [ ] create `sample.env` file with dummy credentials
- [ ] dont use port 5000, use something else
- [ ] find a way for the application to print any problems in MongoDB connection (like bad authentication, connection timeout) without having to test a route for that
- [ ] Don't connect to the database in every module 
<details>
  <summary>Hint</summary>

  Have a separate class that connects for you and returns the `db` object or the `collections` object to where ever you import (that class) and use it
</details>

- [ ] Everyone `url_prefix`s like @PreethiCodes @ `./modules/app_admin.py:19`
- [ ] `modules/app_shorten.py:62` and `modules/app_analytics.py:25` both does 1 thing similar - returing full url given shortcode. I insist that only `modules/app_shorten.py:62` returns URL and calls `modules/app_analytics.py:25` itself. 
<details>
  <summary>Hint</summary>

  Use internal API Calls
</details>

### Module-wise Changes required:

- [ ] `./modules/app_analytics.py` has following changes - CH1, CH2, CH3
- [ ] `./modules/app_bs.py` has following changes - CH4
- [ ] `./modules/app_shorten.py` has following changes - CH5, CH6, CH7

> [!NOTE]
> All CH identifiers are included in comments on the relevant lines describing the required changes.
> Use Ctrl+Shift+F (Windows/Linux) or Cmd+Shift+F (macOS) to search for a specific CH number and quickly navigate to it.

**Open Challenge**
---
- [ ] Every single record under `click_data` in the database has Unknown for `country`, `region`, `city`. Find out why and try to have the backend register some actual data there, like 'Coimbatore, IN`

Let's see who can figure this out first. If you are the one, mark it as completed and give an explaination below. Attach any relevant images if required. 

I'll drop a hint on Wednesday

<details>
  <summary>Hint</summary>

  Wait till Wednesday :))
</details>

### Explaination:

**Fun Challenges**
---
- [ ] Write test scripts. You will define what function/route to test, the sample input and expected output. It checks if the function/route returns the expected output (P.S it's called Black Box Testing)
- [ ] Try to plug it into GitHub Actions such that whenever someone pushes to backend / makes a pull request, it checks if all functions/routes are still sane

I'll drop a hint on Wednesday

<details>
  <summary>Hint</summary>

  Wait till Wednesday :))
</details>

> [!NOTE]
> We will try having next week's todo's in GitHub Issues. It's better in so many ways