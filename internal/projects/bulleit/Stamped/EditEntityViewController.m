//
//  EditEntityViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/27/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "EditEntityViewController.h"

#import "Entity.h"
#import "STCategoryDropdownTableView.h"
#import "UIColor+Stamped.h"

@implementation EditEntityViewController

@synthesize categoryDropdownTableView = categoryDropdownTableView_;
@synthesize categoryDropdownButton = categoryDropdownButton_;
@synthesize categoryDropdownImageView = categoryDropdownImageView_;
@synthesize entityNameTextField = entityNameTextField_;
@synthesize categoryTextField = categoryTextField_;
@synthesize entityObject = entityObject_;
@synthesize addLocationButton = addLocationButton_;
@synthesize addDescriptionButton = addDescriptionButton_;
@synthesize addLocationView = addLocationView_;

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
  categoryDropdownTableView_.hidden = YES;
  categoryDropdownTableView_.alpha = 0.0;
  addLocationView_.hidden = YES;
  addLocationView_.alpha = 0.0;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.categoryDropdownTableView = nil;
  self.categoryDropdownButton = nil;
  self.categoryDropdownImageView = nil;
  self.entityNameTextField = nil;
  self.categoryTextField = nil;
  self.addLocationButton = nil;
  self.addDescriptionButton = nil;
  self.addLocationView = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - UITableViewDelegate Methods.

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  switch (indexPath.row) {
    case STEditCategoryRowFilm:
      categoryDropdownImageView_.image = [UIImage imageNamed:@"edit_film_icon"];
      NSLog(@"Film selected...");
      break;
    case STEditCategoryRowBooks:
      categoryDropdownImageView_.image = [UIImage imageNamed:@"edit_book_icon"];
      NSLog(@"Books...");
      break;
    case STEditCategoryRowFood:
      categoryDropdownImageView_.image = [UIImage imageNamed:@"edit_food_icon"];
      NSLog(@"food...");
      break;
    case STEditCategoryRowMusic:
      categoryDropdownImageView_.image = [UIImage imageNamed:@"edit_music_icon"];
      NSLog(@"music!");
      break;
    case STEditCategoryRowOther:
      categoryDropdownImageView_.image = [UIImage imageNamed:@"edit_other_icon"];
      NSLog(@"Other!");
    default:
      break;
  }
  categoryDropdownButton_.selected = NO;
  [UIView animateWithDuration:0.2 animations:^{
    tableView.alpha = 0.0;
  } completion:^(BOOL completed) {
    tableView.hidden = YES;
  }];
}

#pragma mark - Action methods.

- (IBAction)addLocationButtonPressed:(id)sender {
  if (addLocationButton_ != sender)
    return;

  addLocationView_.hidden = NO;
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
  
  UIButton* button = sender;
  button.selected = YES;
  categoryDropdownTableView_.hidden = NO;
  [UIView animateWithDuration:0.2 animations:^{
    categoryDropdownTableView_.alpha = 1.0;
  }];
  
}

@end
