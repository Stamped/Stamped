//
//  STImageView.m
//  Stamped
//
//  Created by Andrew Bonventre on 9/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "STImageView.h"

#import <QuartzCore/QuartzCore.h>


@interface STImageView ()
- (void)initialize;

@property (nonatomic, retain) NSMutableData* downloadData;
@property (nonatomic, retain) NSURLConnection* connection;
@end

@implementation STImageView

@synthesize imageURL = imageURL_;
@synthesize downloadData = downloadData_;
@synthesize connection = connection_;
@synthesize delegate = delegate_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self)
    [self initialize];
  
  return self;
}

- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self)
    [self initialize];
  
  return self;
}

- (void)dealloc {
  [self.connection cancel];
  self.connection = nil;
  self.downloadData = nil;
  self.imageURL = nil;
  self.delegate = nil;
  [super dealloc];
}

- (void)initialize {
  self.contentMode = UIViewContentModeScaleAspectFit;
  self.backgroundColor = [UIColor whiteColor];
  self.layer.shadowOpacity = 0.25;
  self.layer.shadowOffset = CGSizeZero;
  self.layer.shadowRadius = 1.0;
  if (!CGRectIsNull(self.frame) && !CGRectIsEmpty(self.frame))
    self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
}

- (void)setFrame:(CGRect)frame {
  [super setFrame:frame];
  if (!CGRectIsNull(self.frame) && !CGRectIsEmpty(self.frame))
    self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
}

- (void)setImageURL:(NSString*)imageURL {
  if (![imageURL isEqualToString:imageURL_]) {
    [imageURL_ release];
    imageURL_ = [imageURL copy];
    if (imageURL_) {
      self.downloadData = [NSMutableData data];
      NSURLRequest* request = [NSURLRequest requestWithURL:[NSURL URLWithString:imageURL_]];
      NSURLConnection* connection = [[NSURLConnection alloc] initWithRequest:request
                                                                    delegate:self];
      self.connection = connection;
      [connection release];
    }
    [self setNeedsDisplay];
  }
}

#pragma mark - NSURLConnectionDelegate methods.

- (void)connection:(NSURLConnection*)connection didReceiveData:(NSData*)data {
  [self.downloadData appendData:data];
}

- (void)connection:(NSURLConnection*)connection didFailWithError:(NSError*)error {
  self.downloadData = nil;
}

- (void)connectionDidFinishLoading:(NSURLConnection*)connection {
  self.image = [UIImage imageWithData:self.downloadData];
  self.downloadData = nil;
  if (self.delegate && [(id)self.delegate respondsToSelector:@selector(STImageView:didLoadImage:)]) {
    [self.delegate STImageView:self didLoadImage:self.image];
  }
}

@end
