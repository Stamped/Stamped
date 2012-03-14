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

@interface STGalleryView ()

- (void)commonInit:(id<STGallery>)gallery withDelegate:(id<STViewDelegate>)delegate;

@end

@interface STGalleryItemView : UIView <STImageViewDelegate>

- (id)initWithFrame:(CGRect)frame andGalleryItem:(id<STGalleryItem>)item;

@property (nonatomic, retain) STImageView* image;
@property (nonatomic, retain) NSString* link;
@property (nonatomic, retain) NSString* linkType;
@property (nonatomic, retain) UILabel* caption;

@end

@implementation STGalleryView

- (id)initWithGallery:(id<STGallery>)gallery andDelegate:(id<STViewDelegate>)delegate {
  self = [super initWithFrame:CGRectZero];
  if (self) {
    [self commonInit:gallery withDelegate:delegate];
  }
  return self;
}

- (void)commonInit:(id<STGallery>)gallery withDelegate:(id<STViewDelegate>)delegate {
  self.pagingEnabled = YES;
  self.scrollEnabled = YES;
  self.clipsToBounds = NO;
  self.frame = CGRectMake(30, 0, 260, 360);
  NSInteger offset = 0;
  for (id<STGalleryItem> item in gallery.data) {
    STGalleryItemView* view = [[STGalleryItemView alloc] initWithFrame:CGRectMake(offset, 0, 260, 360) andGalleryItem:item];
    [self addSubview:view];
    offset += 260;
  }
	[self setContentSize:CGSizeMake(offset, 360)];
  //self.backgroundColor = [UIColor blackColor];
}

@end

@implementation STGalleryItemView

@synthesize image = image_;
@synthesize link = link_;
@synthesize linkType = linkType_;
@synthesize caption = caption_;

- (id)initWithFrame:(CGRect)frame andGalleryItem:(id<STGalleryItem>)item {
  self = [super initWithFrame:frame];
  NSLog(@"Here Item");
  if (self) {
    STImageView* view = [[STImageView alloc] initWithFrame:CGRectMake(5, 5, 250, 350)];
    view.imageURL = item.image;
    view.hidden = YES;
    view.backgroundColor = [UIColor clearColor];
    view.layer.shadowOpacity = 0;
    view.delegate = self;
    [self addSubview:view];
    //UILabel* label = [[UILabel alloc] initWithFrame:CGRectMake(10, 10, 80, 80)];
    //label.text = @"Hello";
    //[self addSubview:label];
    //self.backgroundColor = [UIColor redColor];
  }
  return self;
}

- (void)STImageView:(STImageView*)imageView didLoadImage:(UIImage*)image {
  imageView.hidden = NO;
  [self setNeedsDisplay];
  NSLog(@"loaded %@ %f %f", imageView.imageURL,imageView.image.size.width, imageView.image.size.height);
}

@end
