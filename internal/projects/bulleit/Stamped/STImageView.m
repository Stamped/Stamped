//
//  STImageView.m
//  Stamped
//
//  Created by Andrew Bonventre on 9/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "STImageView.h"

#import <QuartzCore/QuartzCore.h>

#import "Notifications.h"

@interface STImageView ()
- (void)initialize;

@property (nonatomic, retain) NSMutableData* downloadData;
@property (nonatomic, retain) NSURLConnection* connection;
@end

@implementation STImageView

@synthesize imageURL = imageURL_;
@synthesize downloadData = downloadData_;
@synthesize connection = connection_;

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
  self.connection = nil;
  self.downloadData = nil;
  self.imageURL = nil;
  [super dealloc];
}

- (void)initialize {
  self.contentMode = UIViewContentModeScaleAspectFit;
  self.backgroundColor = [UIColor whiteColor];
  self.layer.shadowOpacity = 0.25;
  self.layer.shadowOffset = CGSizeZero;
  self.layer.shadowRadius = 1.0;
  self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
}

- (void)setFrame:(CGRect)frame {
  [super setFrame:frame];
  self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
}

- (void)setImageURL:(NSString*)imageURL {
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

#pragma mark - NSURLConnectionDelegate methods.

- (void)connection:(NSURLConnection*)connection didReceiveData:(NSData*)data {
  [self.downloadData appendData:data];
}

- (void)connection:(NSURLConnection*)connection didFailWithError:(NSError*)error {
  self.downloadData = nil;
}

- (void)connectionDidFinishLoading:(NSURLConnection*)connection {
  self.image = [[[UIImage alloc] initWithData:self.downloadData] autorelease];
  self.downloadData = nil;
}

@end
