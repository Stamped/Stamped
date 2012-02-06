//
//  STStampFilterBar.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/9/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "STStampFilterBar.h"

#import <QuartzCore/QuartzCore.h>

#import "STSearchField.h"

static const CGFloat kHorizontalSeparation = 42.0;
static const CGFloat kTopMargin = 7;
static NSString* const kNumInstructionsDisplayed = @"kNumInstructionsDisplayed";

@interface STStampFilterBar ()
- (void)initialize;
- (void)filterButtonPressed:(id)sender;
- (void)searchButtonPressed:(id)sender;
- (void)backButtonPressed:(id)sender;
- (void)fireDelegateMethod;
- (void)addFirstPageButtons;
- (void)addSecondPageButtons;
- (void)showTooltipIfNeeded;
- (UIImageView*)tooltipViewForButton:(UIButton*)button showInstruction:(BOOL)showInstruction;

@property (nonatomic, readonly) UIScrollView* scrollView;
@property (nonatomic, retain) NSMutableArray* filterButtons;
@property (nonatomic, retain) UIButton* searchButton;
@end

@implementation STStampFilterBar

@synthesize delegate = delegate_;
@synthesize scrollView = scrollView_;
@synthesize filterButtons = filterButtons_;
@synthesize filterType = filterType_;
@synthesize searchQuery = searchQuery_;
@synthesize searchField = searchField_;
@synthesize searchButton = searchButton_;
@synthesize tooltipImageView = tooltipImageView_;

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
  self.searchButton = nil;
  searchField_ = nil;
  scrollView_ = nil;
  tooltipImageView_ = nil;
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

  for (UIButton* button in filterButtons_) {
    [button addTarget:self
               action:@selector(filterButtonPressed:)
     forControlEvents:UIControlEventTouchUpInside];
  }
  
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
  searchField_ = [[STSearchField alloc] initWithFrame:CGRectMake(380, 11, 250, 30)];
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

  [self showTooltipIfNeeded];
  [self fireDelegateMethod];
}

- (UIImageView*)tooltipViewForButton:(UIButton*)button showInstruction:(BOOL)showInstruction {
  NSString* imgName = @"tooltip_filter_";
  switch (button.tag) {
    case StampFilterTypeBook:
      imgName = [imgName stringByAppendingString:@"books"];
      break;
    case StampFilterTypeFilm:
      imgName = [imgName stringByAppendingString:@"film"];
      break;
    case StampFilterTypeMusic:
      imgName = [imgName stringByAppendingString:@"music"];
      break;
    case StampFilterTypeFood:
      imgName = [imgName stringByAppendingString:@"food"];
      break;
    case StampFilterTypeOther:
      imgName = [imgName stringByAppendingString:@"other"];
      break;
      
    default:
      NSLog(@"WTF. Can't find %@", imgName);
      break;
  }
  if (showInstruction)
    imgName = [imgName stringByAppendingString:@"_tap"];

  return [[[UIImageView alloc] initWithImage:[UIImage imageNamed:imgName]] autorelease];
}

- (void)fireDelegateMethod {
  searchButton_.selected = searchQuery_.length > 0;

  [delegate_ stampFilterBar:self
            didSelectFilter:filterType_
                   andQuery:searchQuery_];
}

- (void)showTooltipIfNeeded {
  BOOL showInstruction = ([[NSUserDefaults standardUserDefaults] integerForKey:kNumInstructionsDisplayed] < 10);
  if (tooltipImageView_) {
    [tooltipImageView_.layer removeAllAnimations];
    tooltipImageView_.alpha = 1;
    UIImageView* tooltipView = tooltipImageView_;
    tooltipImageView_ = nil;
    [UIView animateWithDuration:0.2
                          delay:0
                        options:UIViewAnimationOptionAllowUserInteraction | UIViewAnimationOptionCurveEaseIn | UIViewAnimationOptionBeginFromCurrentState
                     animations:^{ tooltipView.alpha = 0; }
                     completion:^(BOOL finished) {
                       if (!finished)
                         return;

                       [tooltipView removeFromSuperview];
                     }];
    [self showTooltipIfNeeded];
    return;
  }
  for (UIButton* button in filterButtons_) {
    if (filterType_ == button.tag && button.selected) {
      tooltipImageView_ = [self tooltipViewForButton:button showInstruction:showInstruction];
      tooltipImageView_.alpha = 0;
      CGPoint tooltipCenter = [button.superview convertPoint:button.center toView:self.superview];
      if (filterType_ == StampFilterTypeFood) {
        tooltipCenter.x += 50;
      } else if (filterType_ == StampFilterTypeBook && showInstruction) {
        tooltipCenter.x += 17;
      }
      tooltipCenter.y += (CGRectGetHeight(tooltipImageView_.bounds) / 2) + 2;
      tooltipImageView_.center = tooltipCenter;
      [self.superview addSubview:tooltipImageView_];
      
      [UIView animateWithDuration:0.4
                            delay:0
                          options:UIViewAnimationOptionAllowUserInteraction | UIViewAnimationOptionCurveEaseOut
                       animations:^{
                         tooltipImageView_.alpha = 1;
                         CGPoint center = tooltipImageView_.center;
                         center.y += 7;
                         tooltipImageView_.center = center;
                       }
                       completion:^(BOOL finished) {
                         if (!finished)
                           return;

                         [UIView animateWithDuration:0.2
                                               delay:1.5
                                             options:UIViewAnimationOptionAllowUserInteraction | UIViewAnimationOptionCurveEaseIn
                                          animations:^{ tooltipImageView_.alpha = 0; }
                                          completion:^(BOOL finished) {
                                            if (!finished)
                                              return;
                                            [tooltipImageView_ removeFromSuperview];
                                            tooltipImageView_ = nil;
                                          }];
                       }];
      break;
    }
  }
}

#pragma mark - UIScrollViewDelegate methods.

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
  if (!tooltipImageView_)
    return;

  tooltipImageView_.transform = CGAffineTransformMakeTranslation(-scrollView.contentOffset.x, 0);
}

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

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  [textField resignFirstResponder];
  self.searchQuery = searchField_.text;
  [self fireDelegateMethod];
  return YES;
}

- (BOOL)textField:(UITextField*)textField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString*)string {
  NSString* result = [textField.text stringByReplacingCharactersInRange:range withString:string];
  if (result.length == 0)
    self.searchQuery = nil;

  return YES;
}

- (BOOL)textFieldShouldClear:(UITextField*)textField {
  self.searchQuery = nil;
  return YES;
}

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  [self.delegate stampFilterBarSearchFieldDidBeginEditing];
}

- (void)textFieldDidEndEditing:(UITextField*)textField {
  [self.delegate stampFilterBarSearchFieldDidEndEditing];
  [self fireDelegateMethod];
}

@end
