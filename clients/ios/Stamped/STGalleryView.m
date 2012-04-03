//
//  STGalleryView.m
//  Stamped
//
//  Created by Landon Judkins on 3/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGalleryView.h"
#import "STImageView.h"
#import <QuartzCore/QuartzCore.h>
#import "Util.h"
#import "STPageControl.h"
#import "UIColor+Stamped.h"

static const CGFloat _padding_w = 10;
static const CGFloat _padding_h = 10;

@interface STGalleryView ()

@property (nonatomic, retain) STPageControl* pageControl;

@end

@interface STGalleryItemView : UIView

- (id)initWithFrame:(CGRect)frame image:(UIImage*)image andGalleryItem:(id<STGalleryItem>)item;

@property (nonatomic, retain) NSString* link;
@property (nonatomic, retain) NSString* linkType;
@property (nonatomic, retain) UILabel* caption;

@end

@implementation STGalleryView

@synthesize pageControl = pageControl_;

- (id)initWithGallery:(id<STGallery>)gallery images:(NSDictionary*)images andDelegate:(id<STViewDelegate>)delegate {

  self = [super initWithFrame:CGRectZero];
  if (self) {
    
    CGFloat maxHeight = 0;
    for (UIImage* image in [images allValues]) {
      CGFloat height = image.size.height + 2 * _padding_h;
      if (height > maxHeight) {
        maxHeight = height;
      }
    }
    if (maxHeight > 300) {
      maxHeight = 300;
    }
    
    CGFloat width = 230;
    
    CGSize totalSize = CGSizeMake(width, maxHeight);
    
    UIScrollView* scrollView = [[UIScrollView alloc] initWithFrame:[Util centeredAndBounded:totalSize inFrame:CGRectMake(0, 0, 320, maxHeight)]];
    scrollView.pagingEnabled = YES;
    scrollView.scrollEnabled = YES;
    scrollView.clipsToBounds = NO;
    scrollView.delegate = self;
    NSInteger offset = 0;
    for (NSInteger i = 0; i < [images count]; i++) {
      id<STGalleryItem> item = [gallery.data objectAtIndex:i];
      UIImage* image = [images objectForKey:item.image];
      STGalleryItemView* view = [[STGalleryItemView alloc] initWithFrame:CGRectMake(offset, 0, width, maxHeight) image:image andGalleryItem:item];
      [scrollView addSubview:view];
      [view release];
      offset += width;
    }
    self.pageControl = [[[STPageControl alloc] initWithFrame:CGRectMake(0, 0, 100, 20)] autorelease];
    self.pageControl.radius = 3;
    self.pageControl.defaultColor = [UIColor stampedLightGrayColor];
    self.pageControl.selectedColor = [UIColor stampedDarkGrayColor];
    self.pageControl.spacing = self.pageControl.radius*3.5;
    self.pageControl.numberOfPages = [images count];
    
    CGSize pageControlSize = [self.pageControl sizeForNumberOfPages:self.pageControl.numberOfPages];
    self.pageControl.frame = [Util centeredAndBounded:pageControlSize inFrame:CGRectMake(0, maxHeight, 320, pageControlSize.height)];
    
    scrollView.showsHorizontalScrollIndicator = NO;
    scrollView.showsVerticalScrollIndicator = NO;
    [self addSubview:self.pageControl];
    [scrollView setContentSize:CGSizeMake(offset, maxHeight)];
    [self addSubview:scrollView];
    [scrollView release];
    self.frame = CGRectMake(0, 0, 320, CGRectGetMaxY(self.pageControl.frame)+10);
    
  }
  return self;
}

- (void)dealloc {
  self.pageControl = nil;
  [super dealloc];
}
- (void)scrollViewDidScroll:(UIScrollView *)scrollView {
}

- (void)scrollViewDidEndDecelerating:(UIScrollView *)scrollView {
   NSInteger page = floor(scrollView.contentOffset.x * 1.0 / scrollView.frame.size.width + .5);
   self.pageControl.currentPage = page;
   [self.pageControl setNeedsDisplay];
}
@end

@implementation STGalleryItemView

@synthesize link = link_;
@synthesize linkType = linkType_;
@synthesize caption = caption_;

- (id)initWithFrame:(CGRect)frame image:(UIImage*)image andGalleryItem:(id<STGalleryItem>)item {
  self = [super initWithFrame:frame];
  if (self) {
    CGRect bounds = CGRectMake(_padding_w, _padding_h, frame.size.width - 2 * _padding_w, frame.size.height - 2 * _padding_h);
    CGRect imageFrame = [Util centeredAndBounded:image.size inFrame:bounds];
    UIImageView* view = [[UIImageView alloc] initWithFrame:imageFrame];
    view.image = image;
    view.backgroundColor = [UIColor clearColor];
    [self addSubview:view];
  }
  return self;
}

- (void)dealloc {
  self.link = nil;
  self.linkType = nil;
  self.caption = nil;
  [super dealloc];
}

@end
