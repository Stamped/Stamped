//
//  EditEntityViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/27/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "EditEntityViewController.h"

#import "DetailedEntity.h"
#import "STNavigationBar.h"
#import "UIColor+Stamped.h"

const CGFloat kKeyboardHeight = 217.0;

@interface EditEntityViewController ()
- (void)showOtherView;
- (void)showFoodView;
- (void)showFilmView;
- (void)showMusicView;
- (void)showBookView;
- (void)clearAllFields;
- (void)resignAnyTextField;
- (void)hideCategoryMenu;
- (void)segmentedControlChanged:(id)sender;
- (void)dismissSelf;
- (void)cancelButtonPressed:(id)sender;
- (void)doneButtonPressed:(id)sender;
@end

@implementation EditEntityViewController

@synthesize scrollView = scrollView_;
@synthesize categoryDropdownTableView = categoryDropdownTableView_;
@synthesize categoryDropdownButton = categoryDropdownButton_;
@synthesize categoryDropdownImageView = categoryDropdownImageView_;
@synthesize entityNameTextField = entityNameTextField_;
@synthesize primaryTextField = primaryTextField_;
@synthesize secondaryTextField = secondaryTextField_;
@synthesize tertiaryTextField = tertiaryTextField_;
@synthesize detailedEntity = detailedEntity_;
@synthesize addLocationButton = addLocationButton_;
@synthesize addDescriptionButton = addDescriptionButton_;
@synthesize addLocationView = addLocationView_;
@synthesize streetTextField = streetTextField_;
@synthesize secondStreetTextField = secondStreetTextField_;
@synthesize cityTextField = cityTextField_;
@synthesize stateTextField = stateTextField_;
@synthesize zipTextField = zipTextField_;
@synthesize menuArrow = menuArrow_;
@synthesize descriptionTextField = descriptionTextField_;
@synthesize segmentedControl = segmentedControl_;
@synthesize selectCountryButton = selectCountryButton_;

- (id)init {
  self = [super initWithNibName:@"EditEntityViewController" bundle:nil];
  if (self) {

  }
  return self;
}

- (void)dealloc {
  self.scrollView = nil;
  self.categoryDropdownTableView = nil;
  self.categoryDropdownButton = nil;
  self.categoryDropdownImageView = nil;
  self.entityNameTextField = nil;
  self.primaryTextField = nil;
  self.secondaryTextField = nil;
  self.tertiaryTextField = nil;
  self.addLocationButton = nil;
  self.addDescriptionButton = nil;
  self.addLocationView = nil;
  self.streetTextField = nil;
  self.secondStreetTextField = nil;
  self.cityTextField = nil;
  self.stateTextField = nil;
  self.zipTextField = nil;
  self.menuArrow = nil;
  self.descriptionTextField = nil;
  self.selectCountryButton = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  
  NSLog(@"Category: %@", detailedEntity_.category);
  
  UIBarButtonItem* backButton = [[UIBarButtonItem alloc] initWithTitle:@"Edit"
                                                                 style:UIBarButtonItemStyleBordered
                                                                target:nil
                                                                action:nil];
  [[self navigationItem] setBackBarButtonItem:backButton];
  [backButton release];

  UIBarButtonItem* cancelButton = [[UIBarButtonItem alloc] initWithTitle:@"Cancel"
                                                                   style:UIBarButtonItemStyleBordered
                                                                  target:self
                                                                  action:@selector(cancelButtonPressed:)];
  [self.navigationItem setLeftBarButtonItem:cancelButton];
  [cancelButton release];

  UIBarButtonItem* doneButton = [[UIBarButtonItem alloc] initWithTitle:@"Done"
                                                                 style:UIBarButtonItemStyleDone
                                                                target:self
                                                                action:@selector(doneButtonPressed:)];
  [self.navigationItem setRightBarButtonItem:doneButton];
  [doneButton release];
  
  entityNameTextField_.font = [UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:27];
  categoryDropdownTableView_.alpha = 0.0;
  menuArrow_.alpha = 0.0;
  addLocationView_.alpha = 0.0;
  secondaryTextField_.alpha = 0.0;
  tertiaryTextField_.alpha = 0.0;
  descriptionTextField_.alpha = 0.0;
  segmentedControl_ = [[UISegmentedControl alloc] initWithItems:
      [NSArray arrayWithObjects:@"Restaurant", @"Bar", nil]];
  segmentedControl_.alpha = 0.0;
  segmentedControl_.segmentedControlStyle = UISegmentedControlStyleBar;
  if ([segmentedControl_ conformsToProtocol:@protocol(UIAppearance)]) {
    NSDictionary* titleTextAttributes = [NSDictionary dictionaryWithObjectsAndKeys:(id)[UIColor stampedGrayColor], (id)UITextAttributeTextColor,
                                                                                   (id)[UIColor whiteColor], (id)UITextAttributeTextShadowColor, 
                                                                                   (id)[NSValue valueWithUIOffset:UIOffsetMake(0, 1)], (id)UITextAttributeTextShadowOffset,  nil];
    [segmentedControl_ setTitleTextAttributes:titleTextAttributes forState:UIControlStateNormal];
    NSDictionary* selectedTextAttributes = [NSDictionary dictionaryWithObjectsAndKeys:(id)[UIColor whiteColor], (id)UITextAttributeTextColor,
                                                                                      (id)[UIColor colorWithWhite:0.5 alpha:1.0], (id)UITextAttributeTextShadowColor,
                                                                                      (id)[NSValue valueWithUIOffset:UIOffsetMake(0, -1)], (id)UITextAttributeTextShadowOffset,  nil];
    [segmentedControl_ setTitleTextAttributes:selectedTextAttributes forState:UIControlStateSelected];
    [segmentedControl_ setTitleTextAttributes:selectedTextAttributes forState:UIControlStateHighlighted];
    [segmentedControl_ setTitleTextAttributes:selectedTextAttributes forState:UIControlStateNormal | UIControlStateSelected];
  }
  segmentedControl_.frame = CGRectMake(10, CGRectGetMinY(primaryTextField_.frame) - 2, 299, CGRectGetHeight(segmentedControl_.bounds));
  [primaryTextField_.superview insertSubview:segmentedControl_ belowSubview:categoryDropdownTableView_];
  [segmentedControl_ release];
  [segmentedControl_ addTarget:self
                        action:@selector(segmentedControlChanged:)
              forControlEvents:UIControlEventValueChanged];
  scrollView_.contentSize = self.view.bounds.size;
  
  ((STNavigationBar*)self.navigationController.navigationBar).hideLogo = YES;
  entityNameTextField_.text = detailedEntity_.title;
  descriptionTextField_.text = detailedEntity_.desc;
  streetTextField_.text = detailedEntity_.street;
  secondStreetTextField_.text = detailedEntity_.substreet;
  cityTextField_.text = detailedEntity_.city;
  stateTextField_.text = detailedEntity_.state;
  zipTextField_.text = detailedEntity_.zipcode;
  segmentedControl_.selectedSegmentIndex = 0;

  if ([detailedEntity_.category isEqualToString:@"other"] || selectedCategory_ == STEditCategoryRowOther) {
    [self showOtherView];
    categoryDropdownImageView_.image = [UIImage imageNamed:@"edit_other_icon"];
    selectedCategory_ = STEditCategoryRowOther;
  } else if ([detailedEntity_.category isEqualToString:@"film"] || selectedCategory_ == STEditCategoryRowFilm) {
    [self showFilmView];
    selectedCategory_ = STEditCategoryRowFilm;
    categoryDropdownImageView_.image = [UIImage imageNamed:@"edit_film_icon"];
    primaryTextField_.text = detailedEntity_.cast;
    secondaryTextField_.text = detailedEntity_.director;
    tertiaryTextField_.text = detailedEntity_.year;
    if ([detailedEntity_.subcategory isEqualToString:@"tv"]) {
      segmentedControl_.selectedSegmentIndex = 1;
    }
  } else if ([detailedEntity_.category isEqualToString:@"book"] || selectedCategory_ == STEditCategoryRowBooks) {
    [self showBookView];
    categoryDropdownImageView_.image = [UIImage imageNamed:@"edit_book_icon"];
    primaryTextField_.text = detailedEntity_.author;
    selectedCategory_ = STEditCategoryRowBooks;
  } else if ([detailedEntity_.category isEqualToString:@"food"] || selectedCategory_ == STEditCategoryRowFood) {
    [self showFoodView];
    categoryDropdownImageView_.image = [UIImage imageNamed:@"edit_food_icon"];
    if ([detailedEntity_.subcategory isEqualToString:@"bar"]) {
      segmentedControl_.selectedSegmentIndex = 1;
    }
    selectedCategory_ = STEditCategoryRowFood;
  } else if ([detailedEntity_.category isEqualToString:@"music"] || selectedCategory_ == STEditCategoryRowMusic) {
    [self showMusicView];
    categoryDropdownImageView_.image = [UIImage imageNamed:@"edit_music_icon"];
    if ([detailedEntity_.subcategory isEqualToString:@"song"]) {
      segmentedControl_.selectedSegmentIndex = 1;
    } 
    if ([detailedEntity_.subcategory isEqualToString:@"artist"]) {
      segmentedControl_.selectedSegmentIndex = 2;
    }    
    primaryTextField_.text = detailedEntity_.artist;
    if ([(NSArray*)detailedEntity_.albums count] > 0)
      secondaryTextField_.text = [detailedEntity_.albums objectAtIndex:0];
    selectedCategory_ = STEditCategoryRowMusic;
  } else {
    selectedCategory_ = STEditCategoryRowOther;
  }
  
  if (selectedCategory_ == STEditCategoryRowFood || selectedCategory_ == STEditCategoryRowOther) {
    NSArray* fields = [NSArray arrayWithObjects:streetTextField_, secondStreetTextField_, cityTextField_, stateTextField_, zipTextField_, nil];
    for (UITextField* field in fields) {
      if (field.text.length > 0) {
        [self addLocationButtonPressed:addLocationButton_];
        break;
      }
    }
  }
  if (selectedCategory_ != STEditCategoryRowMusic && descriptionTextField_.text.length > 0)
    [self addDescriptionButtonPressed:addDescriptionButton_];
  
  NSIndexPath* path = [NSIndexPath indexPathForRow:selectedCategory_ inSection:0];
  [categoryDropdownTableView_ selectRowAtIndexPath:path
                                          animated:NO
                                    scrollPosition:UITableViewScrollPositionNone];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.scrollView = nil;
  self.categoryDropdownTableView = nil;
  self.categoryDropdownButton = nil;
  self.categoryDropdownImageView = nil;
  self.entityNameTextField = nil;
  self.primaryTextField = nil;
  self.secondaryTextField = nil;
  self.tertiaryTextField = nil;
  self.addLocationButton = nil;
  self.addDescriptionButton = nil;
  self.addLocationView = nil;
  self.streetTextField = nil;
  self.secondStreetTextField = nil;
  self.cityTextField = nil;
  self.stateTextField = nil;
  self.zipTextField = nil;
  self.menuArrow = nil;
  self.descriptionTextField = nil;
  self.selectCountryButton = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - UITableViewDelegate Methods.

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  selectedCategory_ = indexPath.row;
  [self clearAllFields];
  [UIView animateWithDuration:0.2 animations:^{
    switch (selectedCategory_) {
      case STEditCategoryRowFilm:
        categoryDropdownImageView_.image = [UIImage imageNamed:@"edit_film_icon"];
        [self showFilmView];
        break;
      case STEditCategoryRowBooks:
        categoryDropdownImageView_.image = [UIImage imageNamed:@"edit_book_icon"];
        [self showBookView];
        break;
      case STEditCategoryRowFood:
        categoryDropdownImageView_.image = [UIImage imageNamed:@"edit_food_icon"];
        [self showFoodView];
        break;
      case STEditCategoryRowMusic:
        categoryDropdownImageView_.image = [UIImage imageNamed:@"edit_music_icon"];
        [self showMusicView];
        break;
      case STEditCategoryRowOther:
        categoryDropdownImageView_.image = [UIImage imageNamed:@"edit_other_icon"];
        [self showOtherView];
        break;
      default:
        break;
    }
    categoryDropdownButton_.selected = NO;
    tableView.alpha = 0.0;
    menuArrow_.alpha = 0.0;
  }];
}

#pragma mark - UITextFieldDelegate Methods.

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  [self hideCategoryMenu];
  
  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState
                   animations:^{
                     scrollView_.frame = CGRectOffset(CGRectInset(scrollView_.frame, 0, kKeyboardHeight / 2), 0, -kKeyboardHeight / 2);
                     CGRect frame = [textField.superview convertRect:textField.frame toView:scrollView_];
                     [scrollView_ scrollRectToVisible:frame animated:YES];
                   }
                   completion:nil];

  selectedTextField_ = textField;
}

- (void)textFieldDidEndEditing:(UITextField*)textField {
  selectedTextField_ = nil;
  
  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState
                   animations:^{
                     scrollView_.frame = CGRectOffset(CGRectInset(scrollView_.frame, 0, -kKeyboardHeight / 2), 0, kKeyboardHeight / 2);
                   }
                   completion:nil];
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  [textField resignFirstResponder];
  return YES;
}

#pragma mark - View feng shui depending on type.

- (void)hideCategoryMenu {
  [UIView animateWithDuration:0.2 animations:^{
    categoryDropdownTableView_.alpha = 0.0;
    menuArrow_.alpha = 0.0;
    categoryDropdownButton_.selected = NO;
  }];
}

- (void)resignAnyTextField {
  [selectedTextField_ resignFirstResponder];
  [UIView animateWithDuration:0.2 animations:^{
    self.scrollView.contentInset = UIEdgeInsetsZero;
  }];
}

- (void)clearAllFields {
  primaryTextField_.text = nil;
  secondaryTextField_.text = nil;
  tertiaryTextField_.text = nil;
  streetTextField_.text = nil;
  secondStreetTextField_.text = nil;
  cityTextField_.text = nil;
  stateTextField_.text = nil;
  zipTextField_.text = nil;
  descriptionTextField_.text = nil;
}

- (void)showOtherView {
  primaryTextField_.alpha = 1.0;
  primaryTextField_.placeholder = @"Category";
  secondaryTextField_.alpha = 0.0;
  tertiaryTextField_.alpha = 0.0;
  segmentedControl_.alpha = 0.0;
  addLocationButton_.alpha = 1.0;
  addLocationView_.alpha = 0.0;
  addDescriptionButton_.alpha = 1.0;
  descriptionTextField_.alpha = 0.0;
  CGRect frame = primaryTextField_.frame;
  frame.origin.y = 69;
  primaryTextField_.frame = frame;
  frame = addLocationView_.frame;
  frame.origin.y = 133;
  addLocationView_.frame = frame;
  frame = addDescriptionButton_.frame;
  frame.origin.x = 164;
  frame.origin.y = 133;
  addDescriptionButton_.frame = frame;
  frame = addLocationButton_.frame;
  frame.origin.x = 11;
  frame.origin.y = 133;
  addLocationButton_.frame = frame;
}

- (void)showFoodView {
  primaryTextField_.alpha = 0.0;
  segmentedControl_.alpha = 1.0;
  [UIView setAnimationsEnabled:NO];
  if (segmentedControl_.numberOfSegments == 3)
    [segmentedControl_ removeSegmentAtIndex:2 animated:NO];

  [segmentedControl_ setTitle:@"Restaurant" forSegmentAtIndex:0];
  [segmentedControl_ setTitle:@"Bar" forSegmentAtIndex:1];
  [UIView setAnimationsEnabled:YES];
  addLocationButton_.alpha = 0.0;
  addLocationView_.alpha = 1.0;
  secondaryTextField_.alpha = 0.0;
  tertiaryTextField_.alpha = 0.0;
  addDescriptionButton_.alpha = 1.0;
  descriptionTextField_.alpha = 0.0;
  CGRect frame = addLocationView_.frame;
  frame.origin.y = CGRectGetMaxY(segmentedControl_.frame) + 12;
  addLocationView_.frame = frame;
  frame = addDescriptionButton_.frame;
  frame.origin.x = 10;
  frame.origin.y = 25 + CGRectGetMaxY(addLocationView_.frame);
  addDescriptionButton_.frame = frame;
}

- (void)showFilmView {
  primaryTextField_.alpha = 1.0;
  primaryTextField_.placeholder = @"Cast";
  secondaryTextField_.alpha = 1.0;
  secondaryTextField_.placeholder = @"Director";
  tertiaryTextField_.alpha = 1.0;
  tertiaryTextField_.placeholder = @"Year";
  segmentedControl_.alpha = 1.0;
  addDescriptionButton_.alpha = 1.0;
  descriptionTextField_.alpha = 0.0;
  [UIView setAnimationsEnabled:NO];
  if (segmentedControl_.numberOfSegments == 3)
    [segmentedControl_ removeSegmentAtIndex:2 animated:NO];

  [segmentedControl_ setTitle:@"Film" forSegmentAtIndex:0];
  [segmentedControl_ setTitle:@"TV Series" forSegmentAtIndex:1];
  [UIView setAnimationsEnabled:YES];
  addLocationButton_.alpha = 0.0;
  addLocationView_.alpha = 0.0;
  CGRect frame = primaryTextField_.frame;
  frame.origin.y = CGRectGetMaxY(segmentedControl_.frame) + 20;
  primaryTextField_.frame = frame;
  secondaryTextField_.frame = CGRectOffset(primaryTextField_.frame, 0, 48);
  tertiaryTextField_.frame = CGRectOffset(secondaryTextField_.frame, 0, 48);
  frame = addDescriptionButton_.frame;
  frame.origin.x = 10;
  frame.origin.y = 25 + CGRectGetMaxY(tertiaryTextField_.frame);
  addDescriptionButton_.frame = frame;
}

- (void)showMusicView {
  primaryTextField_.alpha = 1.0;
  primaryTextField_.placeholder = @"Artist";
  secondaryTextField_.alpha = 0.0;
  secondaryTextField_.placeholder = @"Album";
  tertiaryTextField_.alpha = 0.0;
  segmentedControl_.alpha = 1.0;
  [UIView setAnimationsEnabled:NO];
  [segmentedControl_ setTitle:@"Album" forSegmentAtIndex:0];
  [segmentedControl_ setTitle:@"Song" forSegmentAtIndex:1];
  if (segmentedControl_.numberOfSegments < 3) {
    [segmentedControl_ insertSegmentWithTitle:@"Artist" atIndex:2 animated:NO];
  } else {
    [segmentedControl_ setTitle:@"Artist" forSegmentAtIndex:2];
  }
  [UIView setAnimationsEnabled:YES];
  addDescriptionButton_.alpha = 0.0;
  descriptionTextField_.alpha = 0.0;
  addLocationButton_.alpha = 0.0;
  addLocationView_.alpha = 0.0;
  CGRect frame = primaryTextField_.frame;
  frame.origin.y = CGRectGetMaxY(segmentedControl_.frame) + 20;
  primaryTextField_.frame = frame;
  secondaryTextField_.frame = CGRectOffset(primaryTextField_.frame, 0, 48);
}

- (void)showBookView {
  primaryTextField_.alpha = 1.0;
  primaryTextField_.placeholder = @"Author(s)";
  segmentedControl_.alpha = 0.0;
  addLocationButton_.alpha = 0.0;
  addLocationView_.alpha = 0.0;
  secondaryTextField_.alpha = 0.0;
  tertiaryTextField_.alpha = 0.0;
  addDescriptionButton_.alpha = 1.0;
  descriptionTextField_.alpha = 0.0;
  CGRect frame = primaryTextField_.frame;
  frame.origin.y = 69;
  primaryTextField_.frame = frame;
  frame = addDescriptionButton_.frame;
  frame.origin.x = 10;
  frame.origin.y = 32 + CGRectGetMaxY(primaryTextField_.frame);
  addDescriptionButton_.frame = frame;
}

#pragma mark - Segmented control change methods.

- (void)segmentedControlChanged:(id)sender {
  if (sender != segmentedControl_)
    return;
  
  [self resignAnyTextField];
  [UIView animateWithDuration:0.2 animations:^{
    if (selectedCategory_ == STEditCategoryRowMusic) {
      if (segmentedControl_.selectedSegmentIndex == 0) {  // Album
        [self showMusicView];
      } else if (segmentedControl_.selectedSegmentIndex == 1) {  // Song
        primaryTextField_.alpha = 1.0;
        secondaryTextField_.alpha = 1.0;
        tertiaryTextField_.alpha = 0.0;
      } else if (segmentedControl_.selectedSegmentIndex == 2) {  // Artist
        primaryTextField_.alpha = 0.0;
        secondaryTextField_.alpha = 0.0;
        tertiaryTextField_.alpha = 0.0;
      }
    } else if (selectedCategory_ == STEditCategoryRowFilm) {
      if (segmentedControl_.selectedSegmentIndex == 0) {  // Film
        [self showFilmView];
      } else if (segmentedControl_.selectedSegmentIndex == 1) {  // TV Series
        primaryTextField_.alpha = 0.0;
        secondaryTextField_.alpha = 0.0;
        tertiaryTextField_.alpha = 1.0;
        tertiaryTextField_.frame = primaryTextField_.frame;
        CGRect frame = addDescriptionButton_.frame;
        frame.origin.x = 10;
        frame.origin.y = 25 + CGRectGetMaxY(tertiaryTextField_.frame);
        addDescriptionButton_.frame = frame;
      }
    }
  }];
}

- (void)dismissSelf {
  UIViewController* vc = nil;
  if ([self respondsToSelector:@selector(presentingViewController)])
    vc = [(id)self presentingViewController];
  else
    vc = self.parentViewController;

  if (vc && vc.modalViewController)
    [vc dismissModalViewControllerAnimated:YES];
}

#pragma mark - Action methods.

- (IBAction)selectCountryButtonPressed:(id)sender {
  STSelectCountryViewController* vc = [[STSelectCountryViewController alloc] initWithCountryCode:detailedEntity_.countryCode];
  vc.delegate = self;
  [self.navigationController pushViewController:vc animated:YES];
  [vc release];
}

- (void)doneButtonPressed:(id)sender {
  detailedEntity_.title = entityNameTextField_.text;
  detailedEntity_.desc = descriptionTextField_.text;
  detailedEntity_.street = streetTextField_.text;
  detailedEntity_.substreet = secondStreetTextField_.text;
  detailedEntity_.city = cityTextField_.text;
  detailedEntity_.state = stateTextField_.text;
  detailedEntity_.zipcode = zipTextField_.text;
  
  NSString* street = [[NSArray arrayWithObjects:detailedEntity_.street, detailedEntity_.substreet, nil] componentsJoinedByString:@" "];
  NSString* cityStateZip = [[NSArray arrayWithObjects:detailedEntity_.city, detailedEntity_.state, detailedEntity_.zipcode, nil] componentsJoinedByString:@" "];
  street = [street stringByTrimmingCharactersInSet:
      [NSCharacterSet whitespaceAndNewlineCharacterSet]];
  cityStateZip = [cityStateZip stringByTrimmingCharactersInSet:
      [NSCharacterSet whitespaceAndNewlineCharacterSet]];
  if (street.length > 0 && cityStateZip.length > 0) {
    detailedEntity_.address = [[NSArray arrayWithObjects:street, cityStateZip, nil] componentsJoinedByString:@", "];
  } else {
    detailedEntity_.address = street.length > 0 ? street : cityStateZip;
  }
  
  if (detailedEntity_.address)
    detailedEntity_.address = [detailedEntity_.address stringByAppendingFormat:@", %@", detailedEntity_.countryCode];
  
  switch (selectedCategory_) {
    case STEditCategoryRowFilm:
      detailedEntity_.category = @"film";
      detailedEntity_.cast = primaryTextField_.text;
      detailedEntity_.director = secondaryTextField_.text;
      detailedEntity_.year = tertiaryTextField_.text;
      if (segmentedControl_.selectedSegmentIndex == 0) {
        detailedEntity_.subcategory = @"movie";
      } else {
        detailedEntity_.subcategory = @"tv";
      }
      if (detailedEntity_.year.length > 0) {
        detailedEntity_.subtitle = detailedEntity_.year;
      } else {
        detailedEntity_.subtitle =
            segmentedControl_.selectedSegmentIndex == 0 ? @"Film" : @"TV Series";
      }
      break;
    case STEditCategoryRowBooks:
      detailedEntity_.category = @"book";
      detailedEntity_.subcategory = @"book";
      detailedEntity_.author = primaryTextField_.text;
      detailedEntity_.subtitle =
          detailedEntity_.author.length > 0 ? detailedEntity_.author : @"Book";
      break;
    case STEditCategoryRowFood:
      detailedEntity_.category = @"food";
      detailedEntity_.subcategory =
          segmentedControl_.selectedSegmentIndex == 0 ? @"restaurant" : @"bar";
      if (detailedEntity_.address.length > 0) {
        detailedEntity_.subtitle = detailedEntity_.address;
      } else {
        detailedEntity_.subtitle = detailedEntity_.subcategory.capitalizedString;
      }
      break;
    case STEditCategoryRowMusic:
      detailedEntity_.category = @"music";
      if (segmentedControl_.selectedSegmentIndex == 0) {
        detailedEntity_.subcategory = @"album";
        detailedEntity_.artist = primaryTextField_.text;
        detailedEntity_.subtitle =
            detailedEntity_.artist.length > 0 ? detailedEntity_.artist : @"Album";
      } else if (segmentedControl_.selectedSegmentIndex == 1) {
        detailedEntity_.subcategory = @"song";
        detailedEntity_.artist = primaryTextField_.text;
        detailedEntity_.albums = [NSArray arrayWithObjects:(id)secondaryTextField_.text, nil];
        detailedEntity_.subtitle =
            detailedEntity_.artist.length > 0 ? detailedEntity_.artist : @"Song";
      } else {
        detailedEntity_.subcategory = @"artist";
        detailedEntity_.artist = entityNameTextField_.text;
        detailedEntity_.subtitle = @"Artist";
      }
      break;
    case STEditCategoryRowOther:
      detailedEntity_.category = @"other";
      detailedEntity_.subcategory = @"other";
      detailedEntity_.subtitle =
          primaryTextField_.text.length > 0 ? primaryTextField_.text : @"Other";
      break;
    default:
      break;
  }
  [self dismissSelf];
}

- (void)cancelButtonPressed:(id)sender {
  [self dismissSelf];
}

- (IBAction)addDescriptionButtonPressed:(id)sender {
  if (addDescriptionButton_ != sender)
    return;

  [self hideCategoryMenu];
  CGRect frame = descriptionTextField_.frame;
  frame.origin.y = CGRectGetMinY(addDescriptionButton_.frame) - 10;
  descriptionTextField_.frame = frame;
  
  [UIView animateWithDuration:0.2 animations:^{
    if (addLocationButton_.alpha != 0.0) {
      CGRect frame = addLocationButton_.frame;
      frame.origin.y = 25 + CGRectGetMaxY(descriptionTextField_.frame);
      addLocationButton_.frame = frame;
      addLocationView_.frame = CGRectOffset(addLocationView_.frame, 0, 40);
    }
    descriptionTextField_.alpha = 1.0;
    addDescriptionButton_.alpha = 0.0;
  } completion:^(BOOL finished) { [descriptionTextField_ becomeFirstResponder]; }];
}

- (IBAction)addLocationButtonPressed:(id)sender {
  if (addLocationButton_ != sender)
    return;

  [self resignAnyTextField];
  [self hideCategoryMenu];
  [UIView animateWithDuration:0.2 animations:^{
    addLocationButton_.alpha = 0.0;
    addLocationView_.alpha = 1.0;
    CGRect descriptionButtonFrame = addDescriptionButton_.frame;
    descriptionButtonFrame.origin.x = 10;
    descriptionButtonFrame.origin.y = 25 + CGRectGetMaxY(addLocationView_.frame);
    addDescriptionButton_.frame = descriptionButtonFrame;
  }];
}

- (IBAction)categoryDropdownPressed:(id)sender {
  if (sender != categoryDropdownButton_)
    return;

  [self resignAnyTextField];
  UIButton* button = sender;
  button.selected = !button.selected;
  [UIView animateWithDuration:0.2 animations:^{
    categoryDropdownTableView_.alpha = button.selected ? 1.0 : 0.0;
    menuArrow_.alpha = button.selected ? 1.0 : 0.0;
  }];
}

#pragma mark - STSelectCountryViewControllerDelegate methods.

- (void)viewController:(STSelectCountryViewController*)controller
      didSelectCountry:(NSString*)country
                  code:(NSString*)countryCode {
  self.detailedEntity.countryCode = countryCode;
  [selectCountryButton_ setTitle:country forState:UIControlStateNormal];
}

@end
