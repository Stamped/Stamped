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
static const CGFloat kTopMargin = 7;

@interface STStampFilterBar ()
- (void)initialize;
- (void)filterButtonPressed:(id)sender;
- (void)searchButtonPressed:(id)sender;
- (void)backButtonPressed:(id)sender;
- (void)fireDelegateMethod;
- (void)addFirstPageButtons;
- (void)addSecondPageButtons;

@property (nonatomic, readonly) UIScrollView* scrollView;
@property (nonatomic, retain) NSMutableArray* filterButtons;
@property (nonatomic, retain) UIButton* clearFilterButton;
@property (nonatomic, retain) UIButton* searchButton;
@end

@implementation STStampFilterBar

@synthesize delegate = delegate_;
@synthesize scrollView = scrollView_;
@synthesize filterButtons = filterButtons_;
@synthesize filterType = filterType_;
@synthesize searchQuery = searchQuery_;
@synthesize searchField = searchField_;
@synthesize clearFilterButton = clearFilterButton_;
@synthesize searchButton = searchButton_;

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
  self.filterButtons = nil;
  self.searchQuery = nil;
  self.clearFilterButton = nil;
  self.searchButton = nil;
  [super dealloc];
}

- (void)initialize {
  self.filterButtons = [NSMutableArray array];
  
  scrollView_ = [[UIScrollView alloc] initWithFrame:self.bounds];
  scrollView_.contentSize = CGSizeMake(CGRectGetWidth(self.bounds) * 2,
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

  UIImageView* keyline = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"shelf_keyline_horiz"]];
  [self addSubview:keyline];
  [keyline release];
  
  self.filterType = StampFilterTypeNone;
}

- (void)reset {
  self.searchQuery = nil;
  self.filterType = StampFilterTypeNone;
  self.searchField.text = nil;
  [self.scrollView setContentOffset:CGPointZero animated:YES];
}

- (void)setFilterType:(StampFilterType)filterType {
  filterType_ = filterType;

  for (UIButton* button in filterButtons_) {
    if (filterType == button.tag) {
      button.selected = (!button.selected && filterType != StampFilterTypeNone);
      if (!button.selected) {
        filterType_ = StampFilterTypeNone;
      }
    } else {
      button.selected = NO;
    }
  }

  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionAllowUserInteraction | UIViewAnimationOptionBeginFromCurrentState
                   animations:^{ clearFilterButton_.alpha = filterType_ == StampFilterTypeNone ? 0 : 1; }
                   completion:nil];
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
  
  // Divider and search icon.
  UIImageView* divider = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"hdr_separator"]];
  divider.frame = CGRectOffset(divider.frame, 275, 9);
  [scrollView_ addSubview:divider];
  [divider release];
  
  self.searchButton = [UIButton buttonWithType:UIButtonTypeCustom];
  searchButton_.frame = CGRectMake(279, kTopMargin, 40, 40);
  [searchButton_ setImage:[UIImage imageNamed:@"hdr_searchIconOnly_button"]
                 forState:UIControlStateNormal];
  [searchButton_ setImage:[UIImage imageNamed:@"hdr_searchIconOnly_button_selected"]
                 forState:UIControlStateHighlighted];
  [searchButton_ setImage:[UIImage imageNamed:@"hdr_searchIconOnly_button_selected"]
                 forState:UIControlStateSelected];
  [searchButton_ addTarget:self
                    action:@selector(searchButtonPressed:)
          forControlEvents:UIControlEventTouchUpInside];
  [scrollView_ addSubview:searchButton_];
}

- (void)addSecondPageButtons {
  // Back arrow then divider.
  UIButton* prevButton = [UIButton buttonWithType:UIButtonTypeCustom];
  prevButton.frame = CGRectMake(324, kTopMargin, 40, 40);
  [prevButton setImage:[UIImage imageNamed:@"hdr_back_button"]
              forState:UIControlStateNormal];
  [prevButton setImage:[UIImage imageNamed:@"hdr_back_button_selected"]
              forState:UIControlStateHighlighted];
  [prevButton addTarget:self
                 action:@selector(backButtonPressed:)
       forControlEvents:UIControlEventTouchUpInside];
  [scrollView_ addSubview:prevButton];
  
  UIImageView* divider = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"hdr_separator"]];
  divider.frame = CGRectOffset(divider.frame, 365, 9);
  [scrollView_ addSubview:divider];
  [divider release];
  
  // Search field.
  searchField_ = [[STSearchField alloc] initWithFrame:CGRectMake(380, 10, 250, 30)];
  searchField_.delegate = self;
  searchField_.placeholder = @"Search";
  [scrollView_ addSubview:searchField_];
  [searchField_ release];
}

- (void)searchButtonPressed:(id)sender {
  CGFloat nextPage = fmaxf(0, floorf(scrollView_.contentOffset.x / CGRectGetWidth(self.bounds)) + 1);
  [scrollView_ setContentOffset:CGPointMake(nextPage * 320, 0) animated:YES];
}

- (void)backButtonPressed:(id)sender {
  CGFloat previousPage = fmaxf(0, floorf(scrollView_.contentOffset.x / CGRectGetWidth(self.bounds)) - 1);
  [scrollView_ setContentOffset:CGPointMake(previousPage * 320, 0) animated:YES];
}

- (void)filterButtonPressed:(id)sender {
  self.filterType = [(UIButton*)sender tag];
  [self fireDelegateMethod];
}

- (void)fireDelegateMethod {
  searchButton_.selected = searchQuery_.length > 0;

  [delegate_ stampFilterBar:self
            didSelectFilter:filterType_
                   andQuery:searchQuery_];
}

#pragma mark - UIScrollViewDelegate methods.

- (BOOL)scrollViewShouldScrollToTop:(UIScrollView*)scrollView {
  return NO;
}

- (void)scrollViewDidEndScrollingAnimation:(UIScrollView*)scrollView {
  CGFloat currentPage = fmaxf(0, floorf(scrollView_.contentOffset.x / CGRectGetWidth(self.bounds)));
  if (currentPage == 1)
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

@end
