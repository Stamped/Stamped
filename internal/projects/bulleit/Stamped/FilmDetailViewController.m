//
//  BookDetailViewController.m
//  Stamped
//
//  Created by Jake Zien on 9/11/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "FilmDetailViewController.h"

#import <QuartzCore/QuartzCore.h>

#import "DetailedEntity.h"
#import "Entity.h"

@interface FilmDetailViewController ()
- (void)setupMainActionsContainer;
- (void)setupSectionViews;
@end

@implementation FilmDetailViewController

@synthesize affiliateLogoView = affiliateLogoView_;
@synthesize ratingImageView = ratingImageView_;

- (void)dealloc {
  self.affiliateLogoView = nil;
  self.ratingImageView = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];

  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLayoutSubviews {
  [super viewDidLayoutSubviews];
  if (self.ratingImageView.image)
    self.descriptionLabel.frame = CGRectOffset(self.descriptionLabel.frame,
                                               CGRectGetWidth(self.ratingImageView.frame) + 8, 0);
}

- (void)showContents {
  if (!detailedEntity_.length || detailedEntity_.length.intValue == 0) {
    self.descriptionLabel.text = detailedEntity_.subtitle;
  } else {
    NSNumber*  hours = [NSNumber numberWithFloat:detailedEntity_.length.floatValue / 3600.f];
    CGFloat fMinutes = hours.floatValue;
    hours = [NSNumber numberWithInt:floor(hours.floatValue)];
    
    while (fMinutes > 1)
      fMinutes -= 1.f;

    NSNumber* minutes = [NSNumber numberWithFloat:fMinutes * 60.f];
    self.descriptionLabel.text = [NSString stringWithFormat:@"%d hr %d min", hours.intValue, minutes.intValue];
  }

  if (detailedEntity_.rating && ![detailedEntity_.rating isEqualToString:@"UR"]) {
    self.ratingImageView.image = [UIImage imageNamed:[NSString stringWithFormat:@"rating_%@", detailedEntity_.rating]];
    [self.ratingImageView sizeToFit];
    CGRect frame = ratingImageView_.frame;
    frame.origin.y = CGRectGetMaxY(self.titleLabel.frame);
    ratingImageView_.frame = frame;
  }

  if (detailedEntity_.image && detailedEntity_.image.length > 0) {
    self.imageView.imageURL = detailedEntity_.image;
    self.imageView.delegate = self;
    UITapGestureRecognizer* gr = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(imageViewTapped)];
    [self.imageView addGestureRecognizer:gr];
    [gr release];
  } else {
    [self setupMainActionsContainer];
    [self setupSectionViews];
  }
  [self.view setNeedsLayout];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  self.scrollView.contentSize = CGSizeMake(self.view.bounds.size.width, 480);
  self.mainActionButton.hidden = YES;
  self.mainActionLabel.hidden = YES;
  self.mainActionsView.hidden = YES;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.affiliateLogoView = nil;
  self.ratingImageView = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  self.affiliateLogoView.image = [UIImage imageNamed:@"logo_fandango"];
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (IBAction)mainActionButtonPressed:(id)sender {
  if (detailedEntity_.fandangoURL)
    [[UIApplication sharedApplication] openURL:[NSURL URLWithString:detailedEntity_.fandangoURL]];
  else if (detailedEntity_.itunesShortURL)
    [[UIApplication sharedApplication] openURL:[NSURL URLWithString:detailedEntity_.itunesShortURL]];
  else if (detailedEntity_.amazonURL)
    [[UIApplication sharedApplication] openURL:[NSURL URLWithString:detailedEntity_.amazonURL]];
}

#pragma mark - Content Setup (data retrieval & logic to fill views)

- (void)setupMainActionsContainer {
  if (detailedEntity_.fandangoURL) {
    self.mainActionButton.hidden = NO;
    self.mainActionLabel.hidden = NO;
    self.mainActionsView.hidden = NO;
  } else if (detailedEntity_.itunesURL) {
    self.mainActionButton.hidden = NO;
    self.mainActionLabel.hidden = NO;
    self.mainActionsView.hidden = NO;
    self.mainActionLabel.text = @"Download";
    self.affiliateLogoView.frame = CGRectOffset(self.affiliateLogoView.frame, 0.0, -3.0);
    self.affiliateLogoView.image = [UIImage imageNamed:@"logo_itunes"];
  } else if (detailedEntity_.amazonURL) {
    self.mainActionButton.hidden = NO;
    self.mainActionLabel.hidden = NO;
    self.mainActionsView.hidden = NO;
    self.mainActionLabel.text = @"Buy now";
    self.affiliateLogoView.frame = CGRectOffset(self.affiliateLogoView.frame, 0.0, 2.0);
    self.affiliateLogoView.image = [UIImage imageNamed:@"logo_amazon"];
  } else {
    self.mainContentView.frame = CGRectOffset(self.mainContentView.frame, 0, 
                                              -CGRectGetHeight(self.mainActionsView.frame));
  }
}

- (void)setupSectionViews {
  // Synopsis
  if (detailedEntity_.desc && detailedEntity_.desc.length > 0) {
    [self addSectionWithName:@"Synopsis" previewHeight:118.f];
    CollapsibleViewController* section = [sectionsDict_ objectForKey:@"Synopsis"];
    section.collapsedFooterText = [NSString stringWithFormat:@"read more"];
    section.expandedFooterText = @"read less";
    section.footerLabel.text = section.collapsedFooterText;
    section.imageView = self.imageView;
    [section addWrappingText:detailedEntity_.desc forKey:@"desc"];
    CGRect frame = section.arrowView.frame;
    frame.origin = CGPointMake([section.footerLabel.text sizeWithFont:section.footerLabel.font].width + 15.0, section.arrowView.frame.origin.y);
    section.arrowView.frame = frame;    
    self.mainContentView.hidden = NO;
  }

  // Information
  if (detailedEntity_.genre || detailedEntity_.cast || detailedEntity_.director || 
      detailedEntity_.inTheaters || detailedEntity_.releaseDate ) {
    
    CollapsibleViewController* section = [self makeSectionWithName:@"Information"];
    
    if (detailedEntity_.cast && ![detailedEntity_.cast isEqualToString:@""])
      [section addPairedLabelWithName:@"Cast:" 
                                value:detailedEntity_.cast 
                               forKey:@"cast"];
    if (detailedEntity_.director && ![detailedEntity_.director isEqualToString:@""])
      [section addPairedLabelWithName:@"Director:" 
                                value:detailedEntity_.director 
                               forKey:@"director"];
    if (detailedEntity_.genre && ![detailedEntity_.genre isEqualToString:@""])
      [section addPairedLabelWithName:@"Genres:" 
                                value:detailedEntity_.genre.capitalizedString 
                               forKey:@"genre"];
    if (detailedEntity_.inTheaters)
      [section addPairedLabelWithName:@"In Theaters:" 
                                value:detailedEntity_.inTheaters.stringValue 
                               forKey:@"inTheaters"];
    if (detailedEntity_.releaseDate && ![detailedEntity_.releaseDate isEqualToString:@""])
      [section addPairedLabelWithName:@"Open Date:" 
                                value:detailedEntity_.releaseDate
                               forKey:@"releaseDate"];

    if (section.contentDict.objectEnumerator.allObjects.count > 0) {
      [self addSection:section];
      self.mainContentView.hidden = NO;
    }
  }
  
  // Stamped by  
  NSSet* stamps = entityObject_.stamps;
  
  if (stamps.count > 0) {
    [self addSectionStampedBy];
    self.mainContentView.hidden = NO; 
  }
}

#pragma mark - STImageViewDelegate methods.

- (void)STImageView:(STImageView *)imageView didLoadImage:(UIImage *)image {
  self.imageView.contentMode = UIViewContentModeScaleAspectFit;
  self.imageView.layer.backgroundColor = [UIColor clearColor].CGColor;
  self.imageView.hidden = NO;
  self.imageView.layer.shadowOffset = CGSizeMake(0.0, 4.0);
  self.imageView.layer.shadowRadius = 4.0;
  self.imageView.layer.shadowColor = [UIColor blackColor].CGColor;
  self.imageView.layer.shadowOpacity = 0.33;
  CGRect imageFrame = [Util frameForImage:self.imageView.image inImageViewAspectFit:self.imageView];
  self.imageView.layer.shadowPath = [UIBezierPath bezierPathWithRect:imageFrame].CGPath;

  [self setupMainActionsContainer];
  [self setupSectionViews];
}


@end
