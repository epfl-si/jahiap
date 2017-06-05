import pytest

@pytest.fixture
def site(scope="module"):
  """
    Load site only once
  """
  from jahiap import Site
  return Site("./test/dcsl", "dcsl")


class TestSiteProperties:
  """
    Check main properties of DCSL website
  """

  def test_name(self, site):
    assert site.name == "dcsl"

  def test_title(self, site):
    assert site.title == "Data Center Systems Laboratory"

  def test_acronym(self, site):
    assert site.acronym == "DCSL"

  def test_theme(self, site):
    assert site.theme == "ic"

  def test_breadcrumb_title(self, site):
    assert site.breadcrumb_title == "IC"

  def test_breadcrumb_url(self, site):
    assert site.breadcrumb_url == "http://ic.epfl.ch"

  def test_css_url(self, site):
    assert site.css_url == "//static.epfl.ch/v0.23.0/styles/ic-built.css"


class TestSiteStructure:
  """
    Check main elements of DCSL website
  """
  BOXES_PER_PAGES = {
    "DCSL": 3,
    "Team": 9,
    "Publications": 1,
    "Teaching": 1,
    "soNUMA": 2,
    "IX Dataplane Operating System": 3,
    }

  def test_nb_pages(self, site):
    assert len(site.pages) == len(self.BOXES_PER_PAGES)

  def test_page_titles(self, site):
    expected_titles = set(self.BOXES_PER_PAGES.keys())
    titles = set([p.title for p in site.pages])
    assert expected_titles == titles

  def test_nb_boxes(self, site):
    expected_boxes = sum(self.BOXES_PER_PAGES.values())
    boxes = sum([len(p.boxes) for p in site.pages])
    assert expected_boxes == boxes

  def test_nb_files(self, site):
    assert len(site.files) == 27


class TestSidebar:
  """
    Check content of sidebar
  """
  def get_box(self, site):
    return site.sidebar.boxes[0]

  def test_type(self, site):
    assert self.get_box(site).type == "coloredText"

  def test_title(self, site):
    assert self.get_box(site).title == "Competence or skills"

  def test_content(self, site):
    assert "We focus on interdisciplinary systems" in self.get_box(site).content


class TestHomepage:
  """
    Check main properties & some content of DCSL's frontpage
  """

  def test_pid(self, site):
    assert site.homepage.pid == "115349"

  def test_uuid(self, site):
    assert site.homepage.uuid == "51cc1e42-e0d6-4103-8688-2c3f5a31645a"

  def test_original_uuid(self, site):
    assert site.homepage.original_uuid == "99b07ab2-69d7-493d-adb7-bf1c0f4bbb3c"

  def test_url_mapping(self, site):
    assert site.homepage.vanity_url == "dcsl"

  def test_template(self, site):
    assert site.homepage.template == "home"

  def test_primary_type(self, site):
    assert site.homepage.primary_type == "epfl:home"

  def test_title(self, site):
    assert site.homepage.title == "DCSL"

  def test_acl(self, site):
    assert site.homepage.acl == "u:223767:rwa|u:229105:rwa|u:196571:rwa|u:190526:rwa|g:DCSL-unit:rwa|g:guest:r--|g:jahia-admins:rwa|none"

  def test_content(self, site):
    contents = [box.content for box in site.homepage.boxes]
    assert len(contents) == 3
    expected_contents = [
      "files/Servers lab pic.jpg",
      "IX -- a specialized operating system",
      "We would like to thank our sponsors"
    ]
    for content, expected_content in zip(contents, expected_contents):
      assert expected_content in content
