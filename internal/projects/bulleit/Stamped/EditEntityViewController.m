//
//  EditEntityViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/27/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "EditEntityViewController.h"

#import "Entity.h"
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
@end

@implementation EditEntityViewController

@synthesize navBar = navBar_;
@synthesize scrollView = scrollView_;
@synthesize categoryDropdownTableView = categoryDropdownTableView_;
@synthesize categoryDropdownButton = categoryDropdownButton_;
@synthesize categoryDropdownImageView = categoryDropdownImageView_;
@synthesize entityNameTextField = entityNameTextField_;
@synthesize primaryTextField = primaryTextField_;
@synthesize secondaryTextField = secondaryTextField_;
@synthesize tertiaryTextField = tertiaryTextField_;
@synthesize entityObject = entityObject_;
@synthesize addLocationButton = addLocationButton_;
@synthesize addDescriptionButton = addDescriptionButton_;
@synthesize addLocationView = addLocationView_;
@synthesize streetTextField = streetTextField_;
@synthesize secondStreetTextField = secondStreetTextField_;
@synthesize cityTextField = cityTextField_;
@synthesize stateTextField = stateTextField_;
@synthesize zipTextField = zipTextField_;
@synthesize menuArrow = menuArrow_;

@synthesize segmentedControl = segmentedControl_;


- (id)initWithEntity:(Entity*)entityObject {
  self = [super initWithNibName:@"EditEntityViewController" bundle:nil];
  if (self) {
    self.entityObject = entityObject;
  }
  return self;
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];

  entityNameTextField_.font = [UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:27];
  entityNameTextField_.text = entityObject_.title;
  categoryDropdownTableView_.alpha = 0.0;
  menuArrow_.alpha = 0.0;
  addLocationView_.alpha = 0.0;
  secondaryTextField_.alpha = 0.0;
  tertiaryTextField_.alpha = 0.0;
  self.segmentedControl = [[UISegmentedControl alloc] initWithItems:
      [NSArray arrayWithObjects:@"Restaurant", @"Bar", nil]];
  self.segmentedControl.alpha = 0.0;
  self.segmentedControl.tintColor = [UIColor colorWithWhite:0.9 alpha:1.0];
  self.segmentedControl.frame = CGRectMake(10, CGRectGetMinY(primaryTextField_.frame) - 2, 299, 33);
  [primaryTextField_.superview insertSubview:segmentedControl_ belowSubview:categoryDropdownTableView_];
  [segmentedControl_ release];
  NSIndexPath* path = [NSIndexPath indexPathForRow:STEditCategoryRowOther inSection:0];
  [categoryDropdownTableView_ selectRowAtIndexPath:path
                                          animated:NO
                                    scrollPosition:UITableViewScrollPositionNone];
  selectedCategory_ = STEditCategoryRowOther;
  [segmentedControl_ addTarget:self
                        action:@selector(segmentedControlChanged:)
              forControlEvents:UIControlEventValueChanged];
  scrollView_.contentSize = self.view.bounds.size;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.navBar = nil;
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
  self.segmentedControl = nil;
  self.menuArrow = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  navBar_.hideLogo = YES;
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

  CGFloat maxY = 0.0;
  for (UIView* view in scrollView_.subviews) {
    if (view.alpha != 0.0)
      maxY = fmaxf(CGRectGetMaxY(view.frame), maxY);
  }
  CGFloat inset = fmaxf(0, kKeyboardHeight - (scrollView_.contentSize.height - maxY - 10));
  CGFloat yOffset = 0.0;
  if (scrollView_.contentOffset.y == 0 &&
      CGRectGetMaxY(textField.frame) > (CGRectGetHeight(scrollView_.frame) - kKeyboardHeight)) {
    yOffset = inset;
  }
  [UIView animateWithDuration:0.2 animations:^{
    self.scrollView.contentInset = UIEdgeInsetsMake(0, 0, inset, 0);
    if (yOffset > 0)
      self.scrollView.contentOffset = CGPointMake(0, yOffset);
  }];
  selectedTextField_ = textField;
}

- (void)textFieldDidEndEditing:(UITextField*)textField {
  selectedTextField_ = nil;
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
  segmentedControl_.selectedSegmentIndex = -1;
  [UIView setAnimationsEnabled:YES];
  addLocationButton_.alpha = 0.0;
  addLocationView_.alpha = 1.0;
  secondaryTextField_.alpha = 0.0;
  tertiaryTextField_.alpha = 0.0;
  addDescriptionButton_.alpha = 1.0;
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
  [UIView setAnimationsEnabled:NO];
  if (segmentedControl_.numberOfSegments == 3)
    [segmentedControl_ removeSegmentAtIndex:2 animated:NO];

  [segmentedControl_ setTitle:@"Film" forSegmentAtIndex:0];
  [segmentedControl_ setTitle:@"TV Series" forSegmentAtIndex:1];
  segmentedControl_.selectedSegmentIndex = 0;
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
  segmentedControl_.selectedSegmentIndex = 0;
  addDescriptionButton_.alpha = 0.0;
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
    vc = [self presentingViewController];
  else
    vc = self.parentViewController;
  if (vc && vc.modalViewController)
    [vc dismissModalViewControllerAnimated:YES];
}

#pragma mark - Action methods.

- (IBAction)doneButtonPressed:(id)sender {
  entityObject_.title = entityNameTextField_.text;
  switch (selectedCategory_) {
    case STEditCategoryRowFilm:
      entityObject_.category = @"film";
      [self showFilmView];
      break;
    case STEditCategoryRowBooks:
      entityObject_.category = @"book";
      [self showBookView];
      break;
    case STEditCategoryRowFood:
      entityObject_.category = @"food";
      [self showFoodView];
      break;
    case STEditCategoryRowMusic:
      entityObject_.category = @"music";
      break;
    case STEditCategoryRowOther:
      entityObject_.category = @"other";
      break;
    default:
      break;
  }
  [self dismissSelf];
}

- (IBAction)cancelButtonPressed:(id)sender {
  [self dismissSelf];
}

- (IBAction)addDescriptionButtonPressed:(id)sender {
  if (addDescriptionButton_ != sender)
    return;

  [self hideCategoryMenu];
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

@end
