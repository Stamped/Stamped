//
//  STGalleryView.m
//  Stamped
//
//  Created by Landon Judkins on 3/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGalleryView.h"

@interface STGalleryView ()

- (void)commonInit:(id<STGallery>)gallery;

@end

@interface STGalleryItemView : UIView

- (id)initWithFrame:(CGRect)frame andGalleryItem:(id<STGalleryItem>)item;

@property (nonatomic, retain) UIImageView* image;
@property (nonatomic, retain) NSString* link;
@property (nonatomic, retain) NSString* linkType;

@end

@implementation STGalleryView

- (id)initWithGallery:(id<STGallery>)gallery andFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    [self commonInit:gallery];
  }
  return self;
}

- (void)commonInit:(id<STGallery>)gallery {
  self.pagingEnabled = YES;
  NSInteger maxHeight = 0;
}

@end

@implementation STGalleryItemView

- (id)initWithFrame:(CGRect)frame andGalleryItem:(id<STGalleryItem>)item {
  return nil;
}

@end
