//
//  STStampFilterBar.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/9/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STStampFilterBar.h"

static const CGFloat kHorizontalSeparation = 42.0;
static const CGFloat kTopMargin = 5;

@interface STStampFilterBar ()
- (void)initialize;
- (void)filterButtonPressed:(id)sender;
- (void)sortButtonPressed:(id)sender;
- (void)nextButtonPressed:(id)sender;
- (void)backButtonPressed:(id)sender;
- (void)addFirstPageButtons;
- (void)addSecondPageButtons;

@property (nonatomic, readonly) UIScrollView* scrollView;
@end

@implementation STStampFilterBar

@synthesize delegate = delegate_;
@synthesize scrollView = scrollView_;

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

- (void)initialize {
  scrollView_ = [[UIScrollView alloc] initWithFrame:self.bounds];
  scrollView_.contentSize = CGSizeMake(CGRectGetWidth(self.bounds) * 3,
                                       CGRectGetHeight(self.bounds));
  scrollView_.pagingEnabled = YES;
  scrollView_.showsVerticalScrollIndicator = NO;
  scrollView_.showsHorizontalScrollIndicator = NO;
  [self addSubview:scrollView_];
  [scrollView_ release];
  [self addFirstPageButtons];
  [self addSecondPageButtons];
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
  // None.
  ++i;
  filterButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [filterButton setImage:[UIImage imageNamed:@"hdr_filter_clear_button"]
                forState:UIControlStateNormal];
  [filterButton setImage:[UIImage imageNamed:@"hdr_filter_clear_button_selected"]
                forState:UIControlStateSelected];
  filterButton.frame = CGRectMake(5 + (kHorizontalSeparation * i), kTopMargin, 40, 40);
  filterButton.tag = StampFilterTypeNone;
  [scrollView_ addSubview:filterButton];
  
  for (UIView* view in scrollView_.subviews) {
    if ([view isMemberOfClass:[UIButton class]]) {
      [(UIButton*)view addTarget:self
                          action:@selector(filterButtonPressed:)
                forControlEvents:UIControlEventTouchUpInside];
    }
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
  [sortButton addTarget:self
                 action:@selector(sortButtonPressed:)
       forControlEvents:UIControlEventTouchUpInside];
  [scrollView_ addSubview:sortButton];

  // Book.
  ++i;
  sortButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [sortButton setImage:[UIImage imageNamed:@"hdr_sort_location_button"]
              forState:UIControlStateNormal];
  [sortButton setImage:[UIImage imageNamed:@"hdr_sort_location_button_selected"]
              forState:UIControlStateSelected];
  sortButton.frame = CGRectMake(leftMargin + (kHorizontalSeparation * i), kTopMargin, 40, 40);
  sortButton.tag = StampSortTypeDistance;
  [sortButton addTarget:self
                 action:@selector(sortButtonPressed:)
       forControlEvents:UIControlEventTouchUpInside];
  [scrollView_ addSubview:sortButton];

  // Film.
  ++i;
  sortButton = [UIButton buttonWithType:UIButtonTypeCustom];
  [sortButton setImage:[UIImage imageNamed:@"hdr_sort_popular_button"]
              forState:UIControlStateNormal];
  [sortButton setImage:[UIImage imageNamed:@"hdr_sort_popular_button_selected"]
              forState:UIControlStateSelected];
  sortButton.frame = CGRectMake(leftMargin + (kHorizontalSeparation * i), kTopMargin, 40, 40);
  sortButton.tag = StampSortTypePopularity;
  [sortButton addTarget:self
                 action:@selector(sortButtonPressed:)
       forControlEvents:UIControlEventTouchUpInside];
  [scrollView_ addSubview:sortButton];
  
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

- (void)nextButtonPressed:(id)sender {
  CGFloat nextPage = fmaxf(0, floorf(scrollView_.contentOffset.x / CGRectGetWidth(self.bounds)) + 1);
  [scrollView_ setContentOffset:CGPointMake(nextPage * 320, 0) animated:YES];
}

- (void)backButtonPressed:(id)sender {
  CGFloat previousPage = fmaxf(0, floorf(scrollView_.contentOffset.x / CGRectGetWidth(self.bounds)) - 1);
  [scrollView_ setContentOffset:CGPointMake(previousPage * 320, 0) animated:YES];
}

- (void)sortButtonPressed:(id)sender {
  NSLog(@"Sort button pressed.");
}

- (void)filterButtonPressed:(id)sender {
  NSLog(@"Filter button pressed.");
}


@end
