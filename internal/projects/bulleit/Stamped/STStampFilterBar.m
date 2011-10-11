//
//  STStampFilterBar.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/9/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STStampFilterBar.h"

#import "STSearchField.h"

static const CGFloat kHorizontalSeparation = 42.0;
static const CGFloat kTopMargin = 5;

@interface STStampFilterBar ()
- (void)initialize;
- (void)filterButtonPressed:(id)sender;
- (void)sortButtonPressed:(id)sender;
- (void)nextButtonPressed:(id)sender;
- (void)backButtonPressed:(id)sender;
- (void)fireDelegateMethod;
- (void)addFirstPageButtons;
- (void)addSecondPageButtons;
- (void)addThirdPageButtons;

@property (nonatomic, readonly) UIScrollView* scrollView;
@property (nonatomic, readonly) STSearchField* searchField;
@property (nonatomic, retain) NSMutableArray* filterButtons;
@property (nonatomic, retain) NSMutableArray* sortButtons;
@property (nonatomic, retain) UIButton* clearFilterButton;
@property (nonatomic, retain) CLLocationManager* locationManager;
@end

@implementation STStampFilterBar

@synthesize delegate = delegate_;
@synthesize scrollView = scrollView_;
@synthesize sortButtons = sortButtons_;
@synthesize filterButtons = filterButtons_;
@synthesize filterType = filterType_;
@synthesize sortType = sortType_;
@synthesize searchQuery = searchQuery_;
@synthesize searchField = searchField_;
@synthesize clearFilterButton = clearFilterButton_;
@synthesize locationManager = locationManager_;
@synthesize currentLocation = currentLocation_;

- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self) {
    [self initialize];
  }
  return self;
}

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    [self initialize];
  }
  return self;
}

- (void)dealloc {
  self.sortButtons = nil;
  self.filterButtons = nil;
  self.searchQuery = nil;
  self.clearFilterButton = nil;
  self.locationManager.delegate = nil;
  self.locationManager = nil;
  self.currentLocation = nil;
  [super dealloc];
}

- (void)initialize {
  
  self.locationManager = [[[CLLocationManager alloc] init] autorelease];
  self.locationManager.desiredAccuracy = kCLLocationAccuracyHundredMeters;
  self.locationManager.delegate = self;
  
  self.sortButtons = [NSMutableArray array];
  self.filterButtons = [NSMutableArray array];
  
  scrollView_ = [[UIScrollView alloc] initWithFrame:self.bounds];
  scrollView_.contentSize = CGSizeMake(CGRectGetWidth(self.bounds) * 3,
                                       CGRectGetHeight(self.bounds));
  scrollView_.pagingEnabled = YES;
  scrollView_.showsVerticalScrollIndicator = NO;
  scrollView_.showsHorizontalScrollIndicator = NO;
  scrollView_.delegate = self;
  scrollView_.scrollsToTop = NO;
  [self addSubview:scrollView_];
  [scrollView_ release];
  [self addFirstPageButtons];
  [self addSecondPageButtons];
  [self addThirdPageButtons];
  
  self.filterType = StampFilterTypeNone;
  self.sortType = StampSortTypeTime;
}

- (void)setSortType:(StampSortType)sortType {
  sortType_ = sortType;

  if (sortType == StampSortTypeDistance)
    [self.locationManager startUpdatingLocation];
  else
    [self.locationManager stopUpdatingLocation];
  
  for (UIButton* button in sortButtons_)
    button.selected = (button.tag == sortType);
}

- (void)setFilterType:(StampFilterType)filterType {
  filterType_ = filterType;
  
  for (UIButton* button in filterButtons_) {
    if (filterType == button.tag) {
      button.selected = (!button.selected && filterType != StampFilterTypeNone);
      if (!button.selected)
        filterType_ = StampFilterTypeNone;
    } else {
      button.selected = NO;
    }
  }
}

- (void)addFirstPageButtons {
  NSUInteger i = 0;
  // Food.
  UIButton* filterButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [filterButton setImage:[UIImage imageNamed:@"hdr_filter_restaurants_button"]
                forState:UIControlStateNormal];
  [filterButton setImage:[UIImage imageNamed:@"hdr_filter_restaurants_button_selected"]
                forState:UIControlStateSelected];
  filterButton.frame = CGRectMake(5 + (kHorizontalSeparation * i), kTopMargin, 40, 40);
  filterButton.tag = StampFilterTypeFood;
  [scrollView_ addSubview:filterButton];
  [filterButtons_ addObject:filterButton];

  // Book.
  ++i;
  filterButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [filterButton setImage:[UIImage imageNamed:@"hdr_filter_books_button"]
                forState:UIControlStateNormal];
  [filterButton setImage:[UIImage imageNamed:@"hdr_filter_books_button_selected"]
                forState:UIControlStateSelected];
  filterButton.frame = CGRectMake(5 + (kHorizontalSeparation * i), kTopMargin, 40, 40);
  filterButton.tag = StampFilterTypeBook;
  [scrollView_ addSubview:filterButton];
  [filterButtons_ addObject:filterButton];

  // Film.
  ++i;
  filterButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [filterButton setImage:[UIImage imageNamed:@"hdr_filter_movies_button"]
                forState:UIControlStateNormal];
  [filterButton setImage:[UIImage imageNamed:@"hdr_filter_movies_button_selected"]
                forState:UIControlStateSelected];
  filterButton.frame = CGRectMake(5 + (kHorizontalSeparation * i), kTopMargin, 40, 40);
  filterButton.tag = StampFilterTypeFilm;
  [scrollView_ addSubview:filterButton];
  [filterButtons_ addObject:filterButton];

  // Music.
  ++i;
  filterButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [filterButton setImage:[UIImage imageNamed:@"hdr_filter_music_button"]
                forState:UIControlStateNormal];
  [filterButton setImage:[UIImage imageNamed:@"hdr_filter_music_button_selected"]
                forState:UIControlStateSelected];
  filterButton.frame = CGRectMake(5 + (kHorizontalSeparation * i), kTopMargin, 40, 40);
  filterButton.tag = StampFilterTypeMusic;
  [scrollView_ addSubview:filterButton];
  [filterButtons_ addObject:filterButton];

  // Other.
  ++i;
  filterButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [filterButton setImage:[UIImage imageNamed:@"hdr_filter_other_button"]
                forState:UIControlStateNormal];
  [filterButton setImage:[UIImage imageNamed:@"hdr_filter_other_button_selected"]
                forState:UIControlStateSelected];
  filterButton.frame = CGRectMake(5 + (kHorizontalSeparation * i), kTopMargin, 40, 40);
  filterButton.tag = StampFilterTypeOther;
  [scrollView_ addSubview:filterButton];
  [filterButtons_ addObject:filterButton];

  // None.
  ++i;
  self.clearFilterButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [clearFilterButton_ setImage:[UIImage imageNamed:@"hdr_filter_clear_button"]
                      forState:UIControlStateNormal];
  [clearFilterButton_ setImage:[UIImage imageNamed:@"hdr_filter_clear_button_selected"]
                      forState:UIControlStateHighlighted];
  clearFilterButton_.frame = CGRectMake(5 + (kHorizontalSeparation * i), kTopMargin, 40, 40);
  clearFilterButton_.tag = StampFilterTypeNone;
  clearFilterButton_.alpha = 0;
  [scrollView_ addSubview:clearFilterButton_];
  [filterButtons_ addObject:clearFilterButton_];
  
  for (UIButton* button in filterButtons_) {
    [button addTarget:self
               action:@selector(filterButtonPressed:)
     forControlEvents:UIControlEventTouchUpInside];
  }
  
  // Divider and next arrow.
  UIImageView* divider = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"hdr_separator"]];
  divider.frame = CGRectOffset(divider.frame, 275, 8);
  [scrollView_ addSubview:divider];
  [divider release];
  
  UIButton* nextButton = [UIButton buttonWithType:UIButtonTypeCustom];
  nextButton.frame = CGRectMake(279, kTopMargin, 40, 40);
  [nextButton setImage:[UIImage imageNamed:@"hdr_next_button"]
              forState:UIControlStateNormal];
  [nextButton setImage:[UIImage imageNamed:@"hdr_next_button_selected"]
              forState:UIControlStateHighlighted];
  [nextButton addTarget:self
                 action:@selector(nextButtonPressed:)
       forControlEvents:UIControlEventTouchUpInside];
  [scrollView_ addSubview:nextButton];
}

- (void)addSecondPageButtons {
  // Back arrow then divider.
  UIButton* nextButton = [UIButton buttonWithType:UIButtonTypeCustom];
  nextButton.frame = CGRectMake(324, kTopMargin, 40, 40);
  [nextButton setImage:[UIImage imageNamed:@"hdr_back_button"]
              forState:UIControlStateNormal];
  [nextButton setImage:[UIImage imageNamed:@"hdr_back_button_selected"]
              forState:UIControlStateHighlighted];
  [nextButton addTarget:self
                 action:@selector(backButtonPressed:)
       forControlEvents:UIControlEventTouchUpInside];
  [scrollView_ addSubview:nextButton];
  
  UIImageView* divider = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"hdr_separator"]];
  divider.frame = CGRectOffset(divider.frame, 365, 8);
  [scrollView_ addSubview:divider];
  [divider release];
  
  NSUInteger i = 0;
  CGFloat leftMargin = 379;
  // Time.
  UIButton* sortButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [sortButton setImage:[UIImage imageNamed:@"hdr_sort_time_button"]
              forState:UIControlStateNormal];
  [sortButton setImage:[UIImage imageNamed:@"hdr_sort_time_button_selected"]
              forState:UIControlStateSelected];
  sortButton.frame = CGRectMake(leftMargin + (kHorizontalSeparation * i), kTopMargin, 40, 40);
  sortButton.tag = StampSortTypeTime;
  [scrollView_ addSubview:sortButton];
  [sortButtons_ addObject:sortButton];

  // Book.
  ++i;
  sortButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [sortButton setImage:[UIImage imageNamed:@"hdr_sort_location_button"]
              forState:UIControlStateNormal];
  [sortButton setImage:[UIImage imageNamed:@"hdr_sort_location_button_selected"]
              forState:UIControlStateSelected];
  sortButton.frame = CGRectMake(leftMargin + (kHorizontalSeparation * i), kTopMargin, 40, 40);
  sortButton.tag = StampSortTypeDistance;
  [scrollView_ addSubview:sortButton];
  [sortButtons_ addObject:sortButton];

  // Film.
  ++i;
  sortButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [sortButton setImage:[UIImage imageNamed:@"hdr_sort_popular_button"]
              forState:UIControlStateNormal];
  [sortButton setImage:[UIImage imageNamed:@"hdr_sort_popular_button_selected"]
              forState:UIControlStateSelected];
  sortButton.frame = CGRectMake(leftMargin + (kHorizontalSeparation * i), kTopMargin, 40, 40);
  sortButton.tag = StampSortTypePopularity;
  [scrollView_ addSubview:sortButton];
  [sortButtons_ addObject:sortButton];
  
  for (UIButton* button in sortButtons_) {
    [button addTarget:self
               action:@selector(sortButtonPressed:)
     forControlEvents:UIControlEventTouchUpInside];
  }
  
  UIButton* searchButton = [UIButton buttonWithType:UIButtonTypeCustom];
  searchButton.frame = CGRectMake(555, kTopMargin, 80, 40);
  [searchButton setImage:[UIImage imageNamed:@"hdr_search_button"]
                forState:UIControlStateNormal];
  [searchButton setImage:[UIImage imageNamed:@"hdr_search_button_selected"]
                forState:UIControlStateHighlighted];
  [searchButton addTarget:self
                   action:@selector(nextButtonPressed:)
         forControlEvents:UIControlEventTouchUpInside];
  [scrollView_ addSubview:searchButton];
}

- (void)addThirdPageButtons {
  // Back arrow then divider.
  UIButton* nextButton = [UIButton buttonWithType:UIButtonTypeCustom];
  nextButton.frame = CGRectMake(644, kTopMargin, 40, 40);
  [nextButton setImage:[UIImage imageNamed:@"hdr_back_button"]
              forState:UIControlStateNormal];
  [nextButton setImage:[UIImage imageNamed:@"hdr_back_button_selected"]
              forState:UIControlStateHighlighted];
  [nextButton addTarget:self
                 action:@selector(backButtonPressed:)
       forControlEvents:UIControlEventTouchUpInside];
  [scrollView_ addSubview:nextButton];
  
  UIImageView* divider = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"hdr_separator"]];
  divider.frame = CGRectOffset(divider.frame, 685, 8);
  [scrollView_ addSubview:divider];
  [divider release];
  
  // Search field.
  searchField_ = [[STSearchField alloc] initWithFrame:CGRectMake(700, 10, 250, 30)];
  searchField_.delegate = self;
  searchField_.placeholder = @"Search";
  [scrollView_ addSubview:searchField_];
  [searchField_ release];
}

- (void)nextButtonPressed:(id)sender {
  CGFloat nextPage = fmaxf(0, floorf(scrollView_.contentOffset.x / CGRectGetWidth(self.bounds)) + 1);
  [scrollView_ setContentOffset:CGPointMake(nextPage * 320, 0) animated:YES];
}

- (void)backButtonPressed:(id)sender {
  CGFloat previousPage = fmaxf(0, floorf(scrollView_.contentOffset.x / CGRectGetWidth(self.bounds)) - 1);
  [scrollView_ setContentOffset:CGPointMake(previousPage * 320, 0) animated:YES];
}

- (void)sortButtonPressed:(id)sender {
  self.sortType = [(UIButton*)sender tag];
  [self fireDelegateMethod];
}

- (void)filterButtonPressed:(id)sender {
  self.filterType = [(UIButton*)sender tag];
  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionAllowUserInteraction | UIViewAnimationOptionBeginFromCurrentState
                   animations:^{ clearFilterButton_.alpha = filterType_ == StampFilterTypeNone ? 0 : 1; }
                   completion:nil];
  [self fireDelegateMethod];
}

- (void)fireDelegateMethod {
  [delegate_ stampFilterBar:self
            didSelectFilter:filterType_
               withSortType:sortType_
                   andQuery:searchQuery_];
}

#pragma mark - UIScrollViewDelegate methods.

- (BOOL)scrollViewShouldScrollToTop:(UIScrollView*)scrollView {
  return NO;
}

- (void)scrollViewDidEndScrollingAnimation:(UIScrollView*)scrollView {
  CGFloat currentPage = fmaxf(0, floorf(scrollView_.contentOffset.x / CGRectGetWidth(self.bounds)));
  if (currentPage == 2)
    [searchField_ becomeFirstResponder];
  else
    [searchField_ resignFirstResponder];
}

- (void)scrollViewDidEndDecelerating:(UIScrollView*)scrollView {
  [self scrollViewDidEndScrollingAnimation:scrollView];
}

#pragma mark - UITextFieldDelegate methods.

- (BOOL)textField:(UITextField*)textField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString*)string {
  self.searchQuery = [textField.text stringByReplacingCharactersInRange:range withString:string];
  [self fireDelegateMethod];
  return YES;
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  [textField resignFirstResponder];
  self.searchQuery = searchField_.text;
  [self fireDelegateMethod];
  return YES;
}

- (BOOL)textFieldShouldClear:(UITextField*)textField {
  self.searchQuery = nil;
  [self fireDelegateMethod];
  return YES;
}

#pragma mark - CLLocationManagerDelegate methods.

- (void)locationManager:(CLLocationManager*)manager
    didUpdateToLocation:(CLLocation*)newLocation
           fromLocation:(CLLocation*)oldLocation {
  CLLocationDistance distance = [newLocation distanceFromLocation:oldLocation];
  // 160 meters == 0.1 mi.
  if (distance > 160 || !self.currentLocation) {
    self.currentLocation = newLocation;
    [self fireDelegateMethod];
  }
}

@end
