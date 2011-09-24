//
//  BookDetailViewController.m
//  Stamped
//
//  Created by Jake Zien on 9/11/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "FilmDetailViewController.h"

#import <QuartzCore/QuartzCore.h>

#import "Entity.h"

@interface FilmDetailViewController ()
- (void)setupMainActionsContainer;
- (void)setupSectionViews;
@end

@implementation FilmDetailViewController

@synthesize imageView = imageView_;
@synthesize affiliateLogoView = affiliateLogoView_;
@synthesize ratingView = ratingView_;

- (void)dealloc {
  self.imageView = nil;
  self.affiliateLogoView = nil;
  self.ratingView = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
  
  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)showContents {
  if (!entityObject_.length || entityObject_.length.intValue == 0) 
    self.descriptionLabel.text = entityObject_.subtitle;

  else {
    NSNumber*  hours = [NSNumber numberWithFloat: entityObject_.length.floatValue / 3600.f];
    CGFloat fMinutes = hours.floatValue;
    hours = [NSNumber numberWithInt:floor(hours.floatValue)];
    
    while (fMinutes > 1)
      fMinutes -= 1.f;
    NSNumber* minutes = [NSNumber numberWithFloat:fMinutes * 60.f];
    
    self.descriptionLabel.text = [NSString stringWithFormat:@"%d hr %d min", hours.intValue, minutes.intValue];
  }
  
  if (!entityObject_.rating || [entityObject_.rating isEqualToString:@"UR"]) {
    CGRect frame = self.descriptionLabel.frame;
    frame.origin.x = self.titleLabel.frame.origin.x;
    self.descriptionLabel.frame = frame;
  }
  
  else {
    if ([entityObject_.rating isEqualToString:@"G"]) 
      self.ratingView.image = [UIImage imageNamed:@"rating_G"];
    if ([entityObject_.rating isEqualToString:@"PG"]) 
      self.ratingView.image = [UIImage imageNamed:@"rating_PG"];
    if ([entityObject_.rating isEqualToString:@"PG-13"]) 
      self.ratingView.image = [UIImage imageNamed:@"rating_PG-13"];
    if ([entityObject_.rating isEqualToString:@"R"]) 
      self.ratingView.image = [UIImage imageNamed:@"rating_R"];
    if ([entityObject_.rating isEqualToString:@"NC-17"]) 
      self.ratingView.image = [UIImage imageNamed:@"rating_NC-17"];
    
    [self.ratingView sizeToFit];
    
    CGRect frame = self.descriptionLabel.frame;
    frame.origin.x = CGRectGetMaxX(self.ratingView.frame) + 6.f;
    self.descriptionLabel.frame = frame;

  }

  if (entityObject_.image) {
    self.imageView.hidden = NO;
    self.imageView.image = [UIImage imageWithData:[NSData dataWithContentsOfURL:
                                                   [NSURL URLWithString:entityObject_.image]]];
  }

  [self setupMainActionsContainer];
  [self setupSectionViews];
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
  self.imageView = nil;
  self.affiliateLogoView = nil;
  self.ratingView = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  self.categoryImageView.image = [UIImage imageNamed:@"sort_icon_film_0"];
  self.affiliateLogoView.image = [UIImage imageNamed:@"logo_fandango"];
  
  self.imageView.layer.shadowOffset  = CGSizeMake(0.0, 4.0);
  self.imageView.layer.shadowRadius  = 4.0;
  self.imageView.layer.shadowColor   = [UIColor blackColor].CGColor;
  self.imageView.layer.shadowOpacity = 0.33;
  self.imageView.frame = CGRectMake(self.imageView.frame.origin.x, self.imageView.frame.origin.y,
                                    self.imageView.frame.size.width, 144.0);
  self.imageView.contentMode = UIViewContentModeScaleAspectFit;
  
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (IBAction)mainActionButtonPressed:(id)sender {
  [[UIApplication sharedApplication] openURL:
   [NSURL URLWithString:entityObject_.fandangoURL]];
}

#pragma mark - Content Setup (data retrieval & logic to fill views)

- (void)setupMainActionsContainer {
  if (entityObject_.fandangoURL) {
    self.mainActionButton.hidden = NO;
    self.mainActionLabel.hidden  = NO;
    self.mainActionsView.hidden  = NO;
  } else {
    self.mainContentView.frame = CGRectOffset(self.mainContentView.frame, 0, 
                                              -CGRectGetHeight(self.mainActionsView.frame));
  }
}

- (void)setupSectionViews {
  
  // Synopsis
  if (entityObject_.desc) {
        
    [self addSectionWithName:@"Synopsis" previewHeight:118.f];
    CollapsibleViewController* section = [sectionsDict_ objectForKey:@"Synopsis"];
    section.collapsedFooterText = [NSString stringWithFormat:@"read more"];
    section.expandedFooterText = @"read less";
    section.footerLabel.text = section.collapsedFooterText;
    section.imageView = self.imageView;
    [section addWrappingText:entityObject_.desc forKey:@"desc"];
    section.arrowView.frame = CGRectOffset(section.arrowView.frame, 
                                           [section.footerLabel.text sizeWithFont:section.footerLabel.font].width + 8.0, 0);
    
    self.mainContentView.hidden = NO;
  }

  // Information
  if (entityObject_.genre || entityObject_.cast || entityObject_.director || 
      entityObject_.inTheaters || entityObject_.releaseDate ) {
    
    [self addSectionWithName:@"Information"];
    CollapsibleViewController* section = [sectionsDict_ objectForKey:@"Information"];
    
    if (entityObject_.cast)
      [section addPairedLabelWithName:@"Cast:" 
                                value:entityObject_.cast 
                               forKey:@"cast"];
    if (entityObject_.director)
      [section addPairedLabelWithName:@"Director:" 
                                value:entityObject_.director 
                               forKey:@"director"];
    if (entityObject_.genre)
      [section addPairedLabelWithName:@"Genres:" 
                                value:entityObject_.genre 
                               forKey:@"genre"];
    if (entityObject_.inTheaters)
      [section addPairedLabelWithName:@"In Theaters:" 
                                value:entityObject_.inTheaters.stringValue 
                               forKey:@"inTheaters"];
    if (entityObject_.releaseDate)
      [section addPairedLabelWithName:@"Open Date:" 
                                value:entityObject_.releaseDate
                               forKey:@"releaseDate"];

    self.mainContentView.hidden = NO;
  }
  
  // Stamped by  
  NSSet* stamps = entityObject_.stamps;
  
  if (stamps.count > 0) {
    [self addSectionStampedBy];
    self.mainContentView.hidden = NO; 
  }
}


@end
